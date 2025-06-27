import base64
from io import BytesIO
from fastapi import APIRouter
from pydantic import BaseModel, Field
from typing import List, Optional, Dict
from ..model.template_doc import TemplateDoc
from fastapi.responses import StreamingResponse
from ..model.template_bookmark import TemplateBookmark

from app.db import execute_safe_sql
from exceptions.error import ErrorCode
from utils.EditDocxXML import fill_word_bookmark
from utils.LoadAndDelete import delete_bookmark_content
from utils.handle_header_footer import set_header_footer
from exceptions.command_exception import APIException
from .export_doc_view import get_doc_obj_by_template_id
from constants.template_constant import TemplateBookMarkType
from .create_template_view import create_template

router = APIRouter()

class BookmarkItem(BaseModel):
    bm_id: int = Field(None, description="书签唯一ID")
    font: Optional[str] = Field(None, description="字体")
    font_size: Optional[int] = Field(None, description="字号")
    value: Optional[str] = Field(None, description="书签内容")


class InputSchema(BaseModel):
    template_id: int = Field(..., description='模板id')
    bookmark_list: List[BookmarkItem] = Field(None, description='标签名称列表')
    title_list: List[BookmarkItem] = Field(None, description='报告名称')
    header: BookmarkItem = Field(None, description='页眉')
    footer: BookmarkItem = Field(None, description='页脚')
    operation_type: int = Field(None, description='操作类型 0: 预览 1:另存为')
    name: str = Field(None, description='模板名称 当另存为的时候传入')


class DataSchema(BaseModel):
    file_base64: str = Field(..., description='文件base64')


class OutSchema(BaseModel):
    code: int = Field(200, description='状态码')
    message: str = Field('获取成功', description='返回信息')
    data: DataSchema = Field(..., description='返回数据')



@router.post('/update_bookmark', response_model=OutSchema)
async def update_bookmark(data: InputSchema):
    operation_type = data.operation_type
    template = await TemplateDoc.get_or_none(id=data.template_id)
    if not template:
        raise APIException(ErrorCode.TEMPLATE_NOT_FOUND)
    bookmarks_instance = await TemplateBookmark.filter(template_doc_id=data.template_id, is_del=0)
    bookmark_ids = [bookmark.id for bookmark in bookmarks_instance]
    bookmark_id_font_mapping = {i.id : {'id': i.id, 'font': i.font, 'font_size': i.font_size, 'name': i.name, 'type': i.type} for i in bookmarks_instance}

    input_bookmark_info_list = data.bookmark_list
    input_bookmarks_id_list = [i.bm_id for i in input_bookmark_info_list]

    del_bookmark_id_list = list(set(bookmark_ids) - set(input_bookmarks_id_list)) # 取出来要删除的id，不渲染的标签的id

    title_list_id = [i.bm_id for i in data.title_list]
    title_list_id_info_mapping = {i.bm_id: i for i in data.title_list}

    # 去除掉标题的id，因为标题的要单独处理
    del_bookmark_id_list_not_in_title = [i for i in del_bookmark_id_list if i not in title_list_id]

    # input_bookmarks_id_str = ','.join([str(i.bm_id) for i in data.bookmark_list])
    # sql = f"""select template_bookmark.* from template_doc 
    #         inner join template_bookmark on template_doc.id = template_bookmark.template_doc_id where template_doc.id = %s
    #         and template_bookmark.id in ({input_bookmarks_id_str})"""
    # input_bookmarks = await execute_safe_sql(sql, [data.template_id], return_dict=True)

    # 删除标签
    del_bookmark_name_list = []
    if del_bookmark_id_list_not_in_title:
        del_bookmarks_id_str = ','.join([str(i) for i in del_bookmark_id_list_not_in_title])
        sql = f"""select template_bookmark.name from template_doc 
                inner join template_bookmark on template_doc.id = template_bookmark.template_doc_id where template_doc.id = %s
                and template_bookmark.id in ({del_bookmarks_id_str})"""
        del_bookmarks = await execute_safe_sql(sql, [data.template_id], return_dict=True)
        for i in del_bookmarks:
            del_bookmark_name_list.append(i.get('name'))

    doc = await get_doc_obj_by_template_id(template_id=data.template_id)
    for bookmark_name in del_bookmark_name_list:
        doc_stream = delete_bookmark_content(doc=doc, bookmark_name=bookmark_name, output_path=None)

    # 处理标题 
    title_bookmark_instance = await TemplateBookmark.filter(template_doc_id=data.template_id, id__in=title_list_id, is_del = 0)
    for bookmark in title_bookmark_instance:
        name = bookmark.name
        value = title_list_id_info_mapping[bookmark.id].value
        bookmark_type = bookmark.type
        doc_stream = fill_word_bookmark(doc, name, value, bookmark_type)
    
    # 处理替换修改字体和字体大小
    update_bookmark = get_update_bookmark(bookmark_id_font_mapping, [*data.bookmark_list, *data.title_list])
    for bookmark in update_bookmark:
        name = bookmark.get('name')
        font = bookmark.get('font')
        font_size = bookmark.get('font_size')
        bookmark_type = bookmark.get('type')
        doc_stream = fill_word_bookmark(doc, name, value=None, value_type=bookmark_type, font=font, font_size=font_size)

    # 处理页眉页脚
    header_info = data.header
    if header_info:
        set_header_footer(doc, header_text=header_info.value, header_font_name=header_info.font, header_font_size=header_info.font_size)
    footer_info = data.footer
    if footer_info:
        set_header_footer(doc, footer_text=footer_info.value, footer_font_name=footer_info.font, footer_font_size=footer_info.font_size)


    # 保存为 BytesIO 返回
    output_stream = BytesIO()
    doc.save(output_stream)
    output_stream.seek(0)

    # 返回文件
    # return StreamingResponse(output_stream, media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document", headers={
    #     "Content-Disposition": "attachment; filename=filled.docx"
    # })

    # 转换为 base64 字符串
    doc_raw_bytes = output_stream.read()
    base64_str = base64.b64encode(doc_raw_bytes).decode("utf-8")

    if operation_type == 1: # 另存为
        await create_template(data.name, base64_str, doc_raw_bytes)
    
    return {'code': 200, 'message': '模板更新成功', 'data': {'file_base64': base64_str}}

def get_update_bookmark(real_id_font_mapping: Dict[int, BookmarkItem], input_bookmark_list: List[BookmarkItem]):
    """
    拿传入的和实际的对比
    找到修改的并且返回
    """
    update_book_mark = []
    for i in input_bookmark_list:
        i_dict = dict(i)
        if i.bm_id in real_id_font_mapping:
            if real_id_font_mapping[i.bm_id]['font'] != i.font or real_id_font_mapping[i.bm_id]['font_size'] != i.font_size:
                i_dict['name'] = real_id_font_mapping[i.bm_id]['name']
                i_dict['type'] = real_id_font_mapping[i.bm_id]['type']
                update_book_mark.append(i_dict)
    return update_book_mark