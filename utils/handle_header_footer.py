from docx import Document
from docx.shared import Pt
from docx.oxml.ns import qn


def get_header_footer_font_info(doc: Document):
    """
    获取第一页页眉和页脚的字体名称和字号（磅），返回列表形式。
    :return: 字典 {'header': [...], 'footer': [...]}
    """

    section = doc.sections[0]
    header_text, header_info = extract_info(section.header.paragraphs)
    footer_text, footer_info = extract_info(section.footer.paragraphs)

    return {
        "header": {
            "value": header_text,
            "font": header_info["font"],
            "font_size": header_info["font_size"]
        },
        "footer": {
            "value": footer_text,
            "font": footer_info["font"],
            "font_size": footer_info["font_size"]
        }
    }

def extract_info(paragraphs):
        text = "\n".join(p.text for p in paragraphs)
        font_name = None
        font_size = None
        for p in paragraphs:
            for run in p.runs:
                if run.text.strip():
                    font_name = run.font.name
                    if run.font.size:
                        font_size = run.font.size.pt
                    return text, {'font': font_name, 'font_size': font_size}
        return text, {'font': font_name, 'font_size': font_size}


def set_header_footer(doc, header_text=None, footer_text=None, header_font_name="宋体", header_font_size=12, footer_font_name="宋体", footer_font_size=12):
    """
    为所有节设置相同的页眉和页脚（若参数为 None 则清空），并设置字体和字号。
    :param doc: Document 对象
    :param header_text: 页眉文本字符串
    :param footer_text: 页脚文本字符串
    :param font_name: 字体名（默认：宋体）
    :param font_size: 字号（单位：磅，默认：12）
    """

    for section in doc.sections:
        # 设置页眉
        header = section.header
        if header_text is not None:
            for para in header.paragraphs[:]:
                p = para._element
                p.getparent().remove(p)

            para = header.add_paragraph(header_text)
            run = para.runs[0]
            run.font.name = header_font_name
            run.font.size = Pt(header_font_size)
            rFonts = run._element.rPr.get_or_add_rFonts()
            rFonts.set(qn('w:eastAsia'), header_font_name)

        # 设置页脚
        footer = section.footer
        if footer_text is not None:
            for para in footer.paragraphs[:]:
                p = para._element
                p.getparent().remove(p)

            para = footer.add_paragraph(footer_text)
            run = para.runs[0]
            run.font.name = footer_font_name
            run.font.size = Pt(footer_font_size)
            rFonts = run._element.rPr.get_or_add_rFonts()
            rFonts.set(qn('w:eastAsia'), footer_font_name)