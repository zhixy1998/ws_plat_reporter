import os
import concurrent.futures
from io import BytesIO
from typing import Optional

from jinja2 import Environment, FileSystemLoader

# HTML 模板所在目录
_TEMPLATE_DIR = os.path.dirname(os.path.abspath(__file__))

class BaseHtmlReportBuilder:
    """
    基础 HTML -> PDF 渲染引擎。
    管理 Jinja2 初始化与 Playwright PDF 导出逻辑。
    """

    def __init__(self, template_html: Optional[str] = None, template_file: Optional[str] = None):
        self.template_html = template_html
        self.template_file = template_file

        # Jinja2 环境
        self.env = Environment(
            loader=FileSystemLoader(_TEMPLATE_DIR),
            trim_blocks=True,
            lstrip_blocks=True,
        )

    def _build_context(self) -> dict:
        """
        子类必须实现此方法以提供模板数据。
        """
        raise NotImplementedError("子类必须实现 _build_context")

    def _render_html(self) -> str:
        """
        根据环境变量执行渲染。
        """
        context = self._build_context()
        if self.template_html:
            # 数据库中的动态 HTML
            template = self.env.from_string(self.template_html)
        elif self.template_file:
            # 文件系统中的本地 HTML
            template = self.env.get_template(self.template_file)
        else:
            raise ValueError("未提供 template_html 或 template_file")

        return template.render(**context)

    @staticmethod
    def _html_to_pdf(html_str: str) -> bytes:
        """
        提取到独立线程防止与 FastAPI asyncio event loop 冲突
        """
        def _convert_in_thread():
            from playwright.sync_api import sync_playwright
            with sync_playwright() as p:
                try:
                    # 1. 优先尝试系统自带的 Edge (Windows 10/11 默认自带)
                    browser = p.chromium.launch(headless=True, channel='msedge')
                except Exception:
                    try:
                        # 2. 如果没有 Edge，尝试系统自带的 Chrome
                        browser = p.chromium.launch(headless=True, channel='chrome')
                    except Exception:
                        # 3. 最后回退到 Playwright 下载的默认 Chromium（本地开发或打包环境）
                        browser = p.chromium.launch(headless=True)
                        
                page = browser.new_page()
                page.set_content(html_str, wait_until='networkidle')
                pdf_bytes = page.pdf(
                    format='A4',
                    print_background=True,
                    margin={"top": "0", "bottom": "0", "left": "0", "right": "0"}
                )
                browser.close()
                return pdf_bytes

        with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
            future = executor.submit(_convert_in_thread)
            return future.result()

    def build_html(self) -> str:
        """渲染 HTML 字符串（调试用，可在浏览器预览）"""
        return self._render_html()

    def run(self) -> BytesIO:
        """
        执行完整生成链路，返回 PDF 字节流。
        """
        html_str = self._render_html()
        pdf_bytes = self._html_to_pdf(html_str)
        stream = BytesIO(pdf_bytes)
        stream.seek(0)
        return stream
