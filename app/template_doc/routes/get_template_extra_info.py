import importlib
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
from app.template_doc.model.template_extra_info import TemplateExtraInfo
from constants.template_constant import TemplatePageNumType

router = APIRouter()

class InputSchema(BaseModel):
    id: int = Field(..., description='模板id')


class DataSchema(BaseModel):
    title_list: Optional[List[Dict[str, Union[str, int]]]] = Field(None, description='报告名称')
    header: Dict[str, Union[str, int, float, None]] = Field(None, description='页眉')
    footer: Dict[str, Union[str, int, float, None]] = Field(None, description='页脚')
    remark: Dict[str, Union[str, int, float, None]] = Field(None, description='备注')
    page_num_type: str = Field(..., description='页码类型')
    page_num_type_list: List[str] = Field(..., description='页码类型列表')


class OutSchema(BaseModel):
    code: int = Field(0, description='状态码')
    message: str = Field('获取成功', description='返回信息')
    data: DataSchema = Field(..., description='返回数据')

@router.get('/get_template_extra_info', response_model=OutSchema)
@log_response
async def get_template_extra_info(template_id: int):
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
    # template_extra_info = await TemplateExtraInfo.get_or_none(template_doc_id=template_id)

    module_name = "template_structure." + template_name
    try:
        private_mod = importlib.import_module(module_name)
    except Exception as e:
        private_mod = None
    if private_mod and hasattr(private_mod, 'extra_info'):
        extra_info_config = getattr(private_mod, 'extra_info')
        if 'remark' in extra_info_config:
            header_and_footer_info['remark'] = extra_info_config['remark']
        if extra_info_config.get('page_num_type') is not None:
            header_and_footer_info['page_num_type'] = TemplatePageNumType.get_name_desc_by_value(extra_info_config.get('page_num_type'))
    header_and_footer_info['page_num_type_list'] = [k for k, v in TemplatePageNumType.generate_decs_value_map().items()]
    return {'code': 200, 'message': '获取页眉页脚标题成功', 'data': header_and_footer_info}