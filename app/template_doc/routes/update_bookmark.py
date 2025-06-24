
from typing import List, Optional, Dict
from fastapi import APIRouter, Query
from ..model.template_doc import TemplateDoc
from ..model.template_bookmark import TemplateBookmark
from pydantic import BaseModel, Field
from exceptions.error import ErrorCode
from exceptions.command_exception import APIException
from app.db import execute_safe_sql
from .export_doc_view import get_doc_obj_by_template_id
from utils.EditDocxXML import fill_word_bookmark
from constants.template_constant import TemplateBookMarkType

router = APIRouter()

class BookmarkItem(BaseModel):
    bm_id: int = Field(..., description="书签唯一ID")
    font: Optional[str] = Field(None, description="字体")
    font_size: Optional[int] = Field(None, description="字号")


class InputSchema(BaseModel):
    template_id: int = Field(..., description='模板id')
    bookmark_list: List[BookmarkItem] = Field(None, description='标签名称列表')
    title: str = Field(None, description='报告名称')
    header: str = Field(None, description='页眉')
    footer: str = Field(None, description='页脚')


@router.post('/update_bookmark')
async def update_bookmark(data: InputSchema):
    template = await TemplateDoc.get_or_none(id=data.template_id)
    if not template:
        raise APIException(ErrorCode.TemplateNotFound)
    bookmarks_instance = await TemplateBookmark.filter(template_doc_id=data.template_id)
    bookmark_ids = [bookmark.id for bookmark in bookmarks_instance]
    bookmark_id_font_mapping = {i.id : {'id': i.id, 'font': i.font, 'font_size': i.font_size, 'name': i.name} for i in bookmarks_instance}

    input_bookmarks_id_list = [i.bm_id for i in data.bookmark_list]

    del_bookmark_id = list(set(bookmark_ids) - input_bookmarks_id_list) # 取出来要删除的id，不渲染的标签的id


    input_bookmarks_id_str = ','.join([str(i.bm_id) for i in data.bookmark_list])
    sql = f'select template_bookmark.* from template_doc ' \
            'inner join template_bookmark on template_doc.id = template_bookmark.template_doc_id where template_doc.id = %s' \
            f' and template_bookmark.id in ({input_bookmarks_id_str})'
    input_bookmarks = await execute_safe_sql(sql, [data.template_id], return_dict=True)


    update_bookmark = get_update_bookmark(bookmark_id_font_mapping, data.bookmark_list)
    doc = get_doc_obj_by_template_id(template_id=data.template_id)

    for bookmark in update_bookmark:
        name = bookmark.bookmark_nam
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
    
    return {'code': 200, 'message': '模板更新成功'}

def get_update_bookmark(real_id_font_mapping: Dict[int, BookmarkItem], input_bookmark_list: List[BookmarkItem]):
    """
    拿传入的和实际的对比
    找到修改的并且返回
    """
    update_book_mark = []
    for i in input_bookmark_list:
        if i.bm_id in real_id_font_mapping:
            if real_id_font_mapping[i.bm_id]['font'] != i.font or real_id_font_mapping[i.bm_id]['font_size'] != i.font_size:
                i['name'] = real_id_font_mapping[i.bm_id]['name']
                update_book_mark.append(i)