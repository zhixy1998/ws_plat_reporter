
from typing import List, Dict, Union, Optional
from fastapi import APIRouter, Query
from pydantic import BaseModel, Field

from exceptions.error import ErrorCode
from ..model.template_doc import TemplateDoc
from exceptions.command_exception import APIException
from ..model.template_bookmark import TemplateBookmark
from utils.template_utils import get_doc_obj_by_template_id
from utils.get_bookmark_text import get_bookmark_text
from utils.handle_header_footer import get_header_footer_font_info
from utils.log_decorator import log_response
from app.template_doc.model.custom_bookmark import CustomBookmark

router = APIRouter()

class InputSchema(BaseModel):
    id: int = Field(..., description='模板id')


class DataSchema(BaseModel):
    title_list: Optional[List[Dict[str, Union[str, int]]]] = Field(None, description='报告名称')
    header: Dict[str, Union[str, int, None]] = Field(None, description='页眉')
    footer: Dict[str, Union[str, int, None]] = Field(None, description='页脚')
    note: Dict[str, Union[str, int, None]] = Field(None, description='备注')


class OutSchema(BaseModel):
    code: int = Field(0, description='状态码')
    message: str = Field('获取成功', description='返回信息')
    data: DataSchema = Field(..., description='返回数据')

@router.get('/get_template_extra_info', response_model=OutSchema)
@log_response
async def update_template(template_id: int):
    template_instance = await TemplateDoc.get_or_none(id=template_id)
    if not template_instance:
        raise APIException(ErrorCode.TEMPLATE_NOT_FOUND)
    doc = await get_doc_obj_by_template_id(template_id)
    title_bookmark_instances = await TemplateBookmark.filter(template_doc_id=template_id, name__contains='标题', is_del=0)
    title_bookmark_info_list = [{'bm_id': i.id, 'font': i.font, 'font_size': i.font_size, 'name': i.name} for i in title_bookmark_instances]
    title_content_value_list = []
    for title_bookmark_info in title_bookmark_info_list:
        title_content = get_bookmark_text(doc, title_bookmark_info.get('name'))
        title_content_value_list.append({ **title_bookmark_info, 'value': title_content})
        
    
    

    header_and_footer_info = get_header_footer_font_info(doc) 

    header_and_footer_info['title_list'] = title_content_value_list


    # 获取备注
    template_name = template_instance.name
    bookmark_custom_instances = await CustomBookmark.get_or_none(template_doc_id=template_id)

    module_name = "template_structure." + template_name
    try:
        private_mod = importlib.import_module(module_name)
    except Exception as e:
        private_mod = None
    if private_mod and hasattr(private_mod, 'special_bookmark'):
        note_bookmark_name = private_mod.special_bookmark.get('note')
    else:
        note_bookmark_name = '备注'
    note_bookmark_instance = await TemplateBookmark.get_or_none(template_doc_id=template_id, name=note_bookmark_name, is_del=0)
    if note_bookmark_instance:
        note_dict = {'bm_id': note_bookmark_instance.id, 'font': note_bookmark_instance.font, 
        'font_size': note_bookmark_instance.font_size, 'name': note_bookmark_instance.name, 
        'value': bookmark_custom_instances.note if bookmark_custom_instances else ''}
        header_and_footer_info['note'] = note_dict
    return {'code': 200, 'message': '获取页眉页脚标题成功', 'data': header_and_footer_info}