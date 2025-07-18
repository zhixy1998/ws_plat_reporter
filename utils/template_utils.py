import base64
from io import BytesIO
from docx import Document
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
