"""
经典模式 HTML → PDF 渲染引擎。

复用 ClassicFillDataUtils 的数据获取逻辑，
将 contexts 渲染为 HTML，再通过 Playwright 导出 PDF。

使用方式：

    # 预览（真实数据）
    builder = ClassicHtmlBuilder(measure_type='光谱扫描')
    pdf_bytes = await builder.build_from_contexts(contexts)

    # 也支持直接传 contexts 字典（用于 update_bookmark 假预览）
    pdf_bytes = await builder.build_from_contexts(contexts)
"""

import os
import base64
import concurrent.futures

from jinja2 import Environment


def _html_to_pdf(html_str: str, header_template: str = None, footer_template: str = None, pdf_margin: dict = None) -> bytes:
    """
    将 HTML 字符串转换为 PDF 字节流。
    header_template / footer_template: Playwright 页眉页脚 HTML（支持 pageNumber / totalPages 类）
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

            # ---- 浏览器查找逻辑 ----
            if sys.platform == "win32":
                # 优先 Edge
                edge_candidates = [
                    os.path.join(os.environ.get("PROGRAMFILES(X86)", ""), "Microsoft", "Edge", "Application", "msedge.exe"),
                    os.path.join(os.environ.get("PROGRAMFILES", ""), "Microsoft", "Edge", "Application", "msedge.exe"),
                    os.path.join(os.environ.get("LOCALAPPDATA", ""), "Microsoft", "Edge", "Application", "msedge.exe"),
                ]
                edge_path = next((pth for pth in edge_candidates if pth and os.path.exists(pth)), None)
                if edge_path:
                    try:
                        print(f"[Playwright] 使用系统Edge: {edge_path}")
                        browser = p.chromium.launch(
                            executable_path=edge_path,
                            headless=False,
                            args=["--headless=new"],
                        )
                    except Exception as exc:
                        launch_errors.append(f"Edge启动失败: {exc}")

                # 其次 Chrome
                if browser is None:
                    chrome_candidates = [
                        os.path.join(os.environ.get("PROGRAMFILES(X86)", ""), "Google", "Chrome", "Application", "chrome.exe"),
                        os.path.join(os.environ.get("PROGRAMFILES", ""), "Google", "Chrome", "Application", "chrome.exe"),
                        os.path.join(os.environ.get("LOCALAPPDATA", ""), "Google", "Chrome", "Application", "chrome.exe"),
                    ]
                    chrome_path = next((pth for pth in chrome_candidates if pth and os.path.exists(pth)), None)
                    if chrome_path:
                        try:
                            print(f"[Playwright] 使用系统Chrome: {chrome_path}")
                            browser = p.chromium.launch(
                                executable_path=chrome_path,
                                headless=False,
                                args=["--headless=new"],
                            )
                        except Exception as exc:
                            launch_errors.append(f"Chrome启动失败: {exc}")

            # 回退：Playwright 自带 Chromium
            if browser is None:
                try:
                    print("[Playwright] 回退到 Playwright 默认 Chromium")
                    if sys.platform == "win32":
                        browser = p.chromium.launch(headless=False, args=["--headless=new"])
                    else:
                        browser = p.chromium.launch(headless=True)
                except Exception as exc:
                    launch_errors.append(f"Playwright 默认 Chromium 启动失败: {exc}")
                    raise RuntimeError("; ".join(launch_errors)) from exc

            page = browser.new_page()
            page.set_content(html_str, wait_until='networkidle')
            pdf_kwargs = dict(
                format='A4',
                print_background=True,
                margin=pdf_margin or {"top": "0", "bottom": "0", "left": "0", "right": "0"},
            )
            if header_template or footer_template:
                pdf_kwargs['display_header_footer'] = True
                pdf_kwargs['header_template'] = header_template or '<span></span>'
                pdf_kwargs['footer_template'] = footer_template or '<span></span>'
            pdf_bytes = page.pdf(**pdf_kwargs)
            browser.close()
            return pdf_bytes

    with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
        future = executor.submit(_convert_in_thread)
        return future.result()


class ClassicHtmlBuilder:
    """
    经典模式 HTML 渲染器。
    接收数据库中的 HTML Jinja2 模板字符串，渲染 contexts → PDF。
    """

    def __init__(self, template_html: str):
        # Jinja2 环境：trim_blocks 去掉 {% %} 后紧跟的换行，lstrip_blocks 去掉 {% %} 前的缩进空白
        self.env = Environment(trim_blocks=True, lstrip_blocks=True)
        # 把 DB 里的 HTML 字符串（含 {{ }} / {% %} 标记）编译成 Jinja2 模板对象
        self.template = self.env.from_string(template_html)

    def _sanitize_contexts(self, contexts: dict) -> dict:
        """
        清洗 contexts，确保所有值都是 HTML 友好的：
        - None → ''
        - InlineImage/docxtpl 对象 → base64 data URI
        - 其他对象 → str()
        """
        safe = {}
        for k, v in contexts.items():
            if v is None:
                safe[k] = ''
            elif hasattr(v, 'get_src'):  # docxtpl InlineImage
                try:
                    img_stream = v.get_src()
                    img_stream.seek(0)
                    img_bytes = img_stream.read()
                    b64 = base64.b64encode(img_bytes).decode('utf-8')
                    safe[k] = f"data:image/png;base64,{b64}"
                except Exception as e:
                    print(f"[ClassicHtmlBuilder] 无法转换 InlineImage '{k}': {e}")
                    safe[k] = ''
            elif isinstance(v, bytes):
                # 可能是图片字节
                try:
                    b64 = base64.b64encode(v).decode('utf-8')
                    safe[k] = f"data:image/png;base64,{b64}"
                except Exception:
                    safe[k] = str(v)
            elif isinstance(v, str) and v.startswith('data:image'):
                # 已经是 data URI，直接使用
                safe[k] = v
            else:
                safe[k] = v
        return safe

    def render_html(self, contexts: dict) -> str:
        """用 contexts 渲染 HTML 模板，返回 HTML 字符串。"""
        safe_contexts = self._sanitize_contexts(contexts)
        return self.template.render(**safe_contexts)

    def build_pdf(self, contexts: dict) -> bytes:
        """
        完整流程：contexts → HTML → PDF，返回 PDF 字节流。
        从 contexts 中提取 __header__ / __footer__ / __page_num__ 生成页眉页脚页码。
        """
        # 提取页眉页脚配置（从 contexts 移除，避免二次渲染到 body 中）
        header_info = contexts.pop('__header__', None) or {}
        footer_info = contexts.pop('__footer__', None) or {}
        page_num_info = contexts.pop('__page_num__', None) or {}
        margin_info = contexts.pop('__margin__', None) or {}
        orientation_info = contexts.pop('__orientation__', None) or {}
        line_height_info = contexts.pop('__line_height__', None) or {}

        html_str = self.render_html(contexts)
        print(f"[ClassicHtmlBuilder] HTML 渲染完成，长度: {len(html_str)}")

        # 注入动态样式：边距 / 横向 / 行边距
        extra_styles = []
        if margin_info.get('value'):
            extra_styles.append(f"@page {{ margin: {margin_info['value']}mm; }}")
        if orientation_info.get('value') == 1:
            extra_styles.append("@page { size: A4 landscape; }")
        if line_height_info.get('value'):
            extra_styles.append(f"body {{ line-height: {line_height_info['value']}; }}")
        if extra_styles:
            style_tag = f"<style>{' '.join(extra_styles)}</style>"
            html_str = html_str.replace('</head>', f"{style_tag}\n</head>", 1)

        # 构建 Playwright 页眉模板
        header_tpl = None
        header_items = header_info.get('items')
        if header_items:
            # 新格式：固定左中右三槽位（缺位留白，避免 flex space-between 把内容挤偏）
            slots = {it.get('position', 'left'): it for it in header_items}
            parts = ['<div style="display:flex;width:100%;padding:3mm 5mm;">']
            for pos in ('left', 'center', 'right'):
                it = slots.get(pos)
                if it:
                    parts.append(
                        f'<div style="flex:1;font-family:{it.get("font", "宋体")};font-size:{it.get("font_size", 10)}pt;'
                        f'text-align:{pos};">{it.get("value", "")}</div>'
                    )
                else:
                    parts.append('<div style="flex:1;"></div>')
            parts.append('</div>')
            header_tpl = ''.join(parts)
        elif header_info.get('value'):
            hdr_font = header_info.get('font', '宋体')
            hdr_size = header_info.get('font_size', 10)
            hdr_pos = header_info.get('position', 'left')
            header_tpl = (
                f'<div style="font-family:{hdr_font};font-size:{hdr_size}pt;'
                f'text-align:{hdr_pos};width:100%;padding:3mm 5mm;">'
                f'{header_info["value"]}</div>'
            )

        # 构建 Playwright 页脚模板（含页码）：页脚文字在上，页码在下
        footer_tpl = None
        footer_items = footer_info.get('items')
        if footer_items or page_num_info:
            ftr_parts = ['<div style="display:flex;flex-direction:column;width:100%;padding:3mm 5mm;">']
            if footer_items:
                # 新格式：固定左中右三槽位（缺位留白）
                _slots = {it.get('position', 'left'): it for it in footer_items}
                row_parts = ['<div style="display:flex;width:100%;">']
                for _pos in ('left', 'center', 'right'):
                    _it = _slots.get(_pos)
                    if _it:
                        row_parts.append(
                            f'<div style="flex:1;font-family:{_it.get("font", "宋体")};font-size:{_it.get("font_size", 9)}pt;'
                            f'text-align:{_pos};">{_it.get("value", "")}</div>'
                        )
                    else:
                        row_parts.append('<div style="flex:1;"></div>')
                row_parts.append('</div>')
                ftr_parts.append(''.join(row_parts))
            elif footer_info.get('value'):
                ftr_font = footer_info.get('font', '宋体')
                ftr_size = footer_info.get('font_size', 9)
                ftr_pos = footer_info.get('position', 'center')
                ftr_parts.append(
                    f'<div style="font-family:{ftr_font};font-size:{ftr_size}pt;'
                    f'text-align:{ftr_pos};width:100%;">'
                    f'{footer_info["value"]}</div>'
                )
            if page_num_info and page_num_info.get('position'):
                pn_pos = page_num_info['position']
                pn_size = page_num_info.get('font_size', 9)
                pn_font = page_num_info.get('font', '宋体')
                ftr_parts.append(
                    f'<div style="font-family:{pn_font};font-size:{pn_size}pt;'
                    f'text-align:{pn_pos};width:100%;">'
                    f'第 <span class="pageNumber"></span> 页 / 共 <span class="totalPages"></span> 页'
                    f'</div>'
                )
            ftr_parts.append('</div>')
            footer_tpl = ''.join(ftr_parts)

        use_header_footer = bool(header_tpl or footer_tpl)
        pdf_margin = {"top": "15mm", "bottom": "15mm", "left": "18mm", "right": "18mm"} if use_header_footer else {"top": "0", "bottom": "0", "left": "0", "right": "0"}

        pdf_bytes = _html_to_pdf(html_str, header_template=header_tpl, footer_template=footer_tpl, pdf_margin=pdf_margin)
        print(f"[ClassicHtmlBuilder] PDF 生成完成，大小: {len(pdf_bytes)} bytes")
        return pdf_bytes

    def build_pdf_base64(self, contexts: dict) -> str:
        """
        完整流程：contexts → HTML → PDF → base64 data URI。
        """
        pdf_bytes = self.build_pdf(contexts)
        b64 = base64.b64encode(pdf_bytes).decode('utf-8')
        return f"data:application/pdf;base64,{b64}"
