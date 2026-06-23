import os
import concurrent.futures
from io import BytesIO
from typing import Dict, Optional, Tuple

from jinja2 import Environment, FileSystemLoader

from config import config

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
    def _find_windows_browser_executable() -> Tuple[Optional[str], Optional[str]]:
        browser_candidates = [
            (
                "Edge",
                [
                    os.path.join(os.environ.get("PROGRAMFILES(X86)", ""), "Microsoft", "Edge", "Application", "msedge.exe"),
                    os.path.join(os.environ.get("PROGRAMFILES", ""), "Microsoft", "Edge", "Application", "msedge.exe"),
                    os.path.join(os.environ.get("LOCALAPPDATA", ""), "Microsoft", "Edge", "Application", "msedge.exe"),
                ],
            ),
            (
                "Chrome",
                [
                    os.path.join(os.environ.get("PROGRAMFILES(X86)", ""), "Google", "Chrome", "Application", "chrome.exe"),
                    os.path.join(os.environ.get("PROGRAMFILES", ""), "Google", "Chrome", "Application", "chrome.exe"),
                    os.path.join(os.environ.get("LOCALAPPDATA", ""), "Google", "Chrome", "Application", "chrome.exe"),
                ],
            ),
        ]

        for browser_name, candidate_paths in browser_candidates:
            for candidate_path in candidate_paths:
                if candidate_path and os.path.exists(candidate_path):
                    return browser_name, candidate_path

        return None, None

    @staticmethod
    def _get_configured_browser_executable() -> Tuple[Optional[str], Optional[str]]:
        browser_path = config.browser_executable_path
        if not browser_path:
            return None, None

        if os.path.exists(browser_path):
            return "配置浏览器", browser_path

        return "配置浏览器", None

    @staticmethod
    def _build_launch_kwargs(executable_path: Optional[str] = None) -> Dict[str, object]:
        launch_kwargs: Dict[str, object] = {}
        if executable_path:
            launch_kwargs["executable_path"] = executable_path

        if os.name == "nt":
            launch_kwargs["headless"] = False
            launch_kwargs["args"] = ["--headless=new"]
        else:
            launch_kwargs["headless"] = True

        return launch_kwargs

    @staticmethod
    def _launch_browser(playwright_instance, executable_path: Optional[str] = None):
        return playwright_instance.chromium.launch(
            **BaseHtmlReportBuilder._build_launch_kwargs(executable_path=executable_path)
        )

    @staticmethod
    def _html_to_pdf(html_str: str) -> bytes:
        """
        提取到独立线程防止与 FastAPI asyncio event loop 冲突
        """
        def _convert_in_thread():
            import sys
            import asyncio
            if sys.platform == "win32":
                asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
                
            from playwright.sync_api import sync_playwright
            with sync_playwright() as p:
                browser = None
                launch_errors = []

                if sys.platform == "win32":
                    browser_name, browser_path = BaseHtmlReportBuilder._find_windows_browser_executable()
                    if browser_name == "Edge" and browser_path:
                        try:
                            print(f"[Playwright] 使用系统{browser_name}: {browser_path}")
                            browser = BaseHtmlReportBuilder._launch_browser(
                                p,
                                executable_path=browser_path,
                            )
                        except Exception as exc:
                            launch_errors.append(f"系统{browser_name}启动失败: {exc}")

                    if browser is None:
                        chrome_candidates = [
                            os.path.join(os.environ.get("PROGRAMFILES(X86)", ""), "Google", "Chrome", "Application", "chrome.exe"),
                            os.path.join(os.environ.get("PROGRAMFILES", ""), "Google", "Chrome", "Application", "chrome.exe"),
                            os.path.join(os.environ.get("LOCALAPPDATA", ""), "Google", "Chrome", "Application", "chrome.exe"),
                        ]
                        chrome_path = next((path for path in chrome_candidates if path and os.path.exists(path)), None)
                        if chrome_path:
                            try:
                                print(f"[Playwright] 使用系统Chrome: {chrome_path}")
                                browser = BaseHtmlReportBuilder._launch_browser(
                                    p,
                                    executable_path=chrome_path,
                                )
                            except Exception as exc:
                                launch_errors.append(f"系统Chrome启动失败: {exc}")
                        else:
                            launch_errors.append("未找到系统 Chrome 可执行文件")

                    if browser is None:
                        configured_browser_name, configured_browser_path = BaseHtmlReportBuilder._get_configured_browser_executable()
                        if configured_browser_path:
                            try:
                                print(f"[Playwright] 使用{configured_browser_name}: {configured_browser_path}")
                                browser = BaseHtmlReportBuilder._launch_browser(
                                    p,
                                    executable_path=configured_browser_path,
                                )
                            except Exception as exc:
                                launch_errors.append(f"{configured_browser_name}启动失败: {exc}")
                        elif configured_browser_name:
                            launch_errors.append(f"配置的浏览器路径不存在: {config.browser_executable_path}")

                if browser is None:
                    try:
                        print("[Playwright] 回退到 Playwright 默认 Chromium")
                        browser = BaseHtmlReportBuilder._launch_browser(p)
                    except Exception as exc:
                        launch_errors.append(f"Playwright 默认 Chromium 启动失败: {exc}")
                        raise RuntimeError("; ".join(launch_errors)) from exc
                        
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
