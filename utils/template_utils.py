import base64
from io import BytesIO
from docx import Document
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

from app.template_doc.model.template_doc import TemplateDoc


async def get_doc_obj_by_template_id(template_id: int):
    template = await TemplateDoc.get_or_none(id=template_id)
    if not template:
        return {'code': 1, 'message': '模板不存在'}
    # 2. base64 解码成二进制
    content_bytes = base64.b64decode(template.template_content)
    doc_stream = BytesIO(content_bytes)
    doc = Document(doc_stream)
    return doc

async def get_doc_name_and_doc_stream_obj(template_id: int):

    template = await TemplateDoc.get_or_none(id=template_id)
    if not template:
        return {'code': 1, 'message': '模板不存在'}
    # 2. base64 解码成二进制
    content_bytes = base64.b64decode(template.template_content)
    doc_stream = BytesIO(content_bytes)
    return template.name, doc_stream


def add_section_page_break(document):
    """
    在文档最后加一个分页的 section break，避免空白页。
    """
    # 添加一个空段落
    p = document.add_paragraph()
    
    # 设置段落为 section break (next page)
    p._p.get_or_add_pPr()
    sectPr = OxmlElement('w:sectPr')
    type_ = OxmlElement('w:type')
    type_.set(qn('w:val'), 'nextPage')
    sectPr.append(type_)
    p._p.get_or_add_pPr().append(sectPr)


def remove_empty_paragraphs_at_end(doc):
    """
    移除文档末尾的空段落，避免产生多余的空白页
    """
    # 获取文档的所有段落
    paragraphs = doc.paragraphs
    
    # 从后往前遍历，移除末尾的空段落
    while paragraphs and (not paragraphs[-1].text.strip() or paragraphs[-1].text == ''):
        # 获取最后一个段落的XML元素
        last_para = paragraphs[-1]
        # 从父元素中移除这个段落
        last_para._element.getparent().remove(last_para._element)
        # 重新获取段落列表
        paragraphs = doc.paragraphs

def remove_last_section_break(doc):
    """
    移除文档末尾的分节符，避免产生空白页
    """
    # 获取文档的最后一个段落
    if doc.paragraphs:
        last_para = doc.paragraphs[-1]
        # 检查段落是否包含分节符
        pPr = last_para._p.get_or_add_pPr()
        sectPr = pPr.find(qn('w:sectPr'))
        if sectPr is not None:
            # 移除分节符
            pPr.remove(sectPr)

def clean_document_for_merge(doc):
    """
    清理文档以便合并，移除可能导致空白页的元素
    """
    # 移除末尾的空段落
    remove_empty_paragraphs_at_end(doc)
    
    # 移除末尾的分节符
    remove_last_section_break(doc)
    
    return doc