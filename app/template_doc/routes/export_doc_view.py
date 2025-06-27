import base64
from io import BytesIO

from docx import Document
from typing import List, Union
from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
from ..model.template_doc import TemplateDoc
from utils.EditDocxXML import fill_word_bookmark
from constants.template_constant import TemplateBookMarkType

router = APIRouter()

class BookmarkData(BaseModel):
    bookmark_name: str
    value: Union[str, List[List[Union[str, int]]]]
    type: int = Field(..., description='0: 文本，1: 表格，2: 图片')

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "bookmark_name": "bookmark_name",
                    "type": 0,
                    "value": "文字"
                },  
                {
                    "type": "bookmark_name",
                    "type": 2,
                    "value": "图片base64"
                },
                {
                    "bookmark_name": "bookmark_name",
                    "type": 1,
                    "value": [["列1", "列2"], ["值1", "值2"]]
                }
            ]
        }
    }

class InputSchema(BaseModel):
    template_id: int = Field(..., description='模板id')
    bookmark_data: List[BookmarkData] = Field(..., description="书签值，支持文本、图片base64、表格数据")

@router.post('/export_doc')
async def export_docx(data: InputSchema):
    template_id = data.template_id
    bookmark_data = data.bookmark_data
    doc = get_doc_obj_by_template_id(template_id)

    for bookmark in bookmark_data:
        name = bookmark.bookmark_name
        value = bookmark.value
        bookmark_type = bookmark.type
        # if bookmark_type == TemplateBookMarkType.text.value:
        #     doc_stream = fill_word_bookmark(doc, name, value)
        if bookmark_type == TemplateBookMarkType.sheet.value:
            doc_stream = fill_word_bookmark(doc, name, value, bookmark_type)
        elif bookmark_type == TemplateBookMarkType.img.value:
            doc_stream = fill_word_bookmark(doc, name, value, bookmark_type)
        else:
            doc_stream = fill_word_bookmark(doc, name, value, bookmark_type)

    # 保存为 BytesIO 返回
    output_stream = BytesIO()
    doc.save(output_stream)
    output_stream.seek(0)

    # 返回文件
    return StreamingResponse(doc_stream, media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document", headers={
        "Content-Disposition": "attachment; filename=filled.docx"
    })

async def get_doc_obj_by_template_id(template_id: int):
    template = await TemplateDoc.get_or_none(id=template_id)
    if not template:
        return {'code': 1, 'message': '模板不存在'}
    # 2. base64 解码成二进制
    content_bytes = base64.b64decode(template.template_content)
    doc_stream = BytesIO(content_bytes)
    doc = Document(doc_stream)
    return doc