import importlib
from typing import List, Dict, Union, Optional
from fastapi import APIRouter, Query
from pydantic import BaseModel, Field

from tortoise import connections
from exceptions.error import ErrorCode
from ..model.template_doc import TemplateDoc
from exceptions.command_exception import APIException
from ..model.template_bookmark import TemplateBookmark
from utils.template_utils import get_doc_obj_by_template_id
from utils.get_bookmark_text import get_bookmark_text
from utils.handle_header_footer import get_header_footer_font_info
from utils.log_decorator import log_response
from constants.template_constant import TemplatePageNumType, MeasureMode, TemplateFootAndHeaderType
from config import config

router = APIRouter()


def _position_to_desc(position: str) -> str:
    """将 CSS position ('left'/'center'/'right') 转为 TemplateFootAndHeaderType 描述文本。"""
    _POS_TO_VALUE = {
        'left': TemplateFootAndHeaderType.left.value,
        'center': TemplateFootAndHeaderType.center.value,
        'right': TemplateFootAndHeaderType.right.value,
    }
    value = _POS_TO_VALUE.get(position)
    if value is not None:
        return TemplateFootAndHeaderType.get_name_desc_by_value(value)
    return '居中展示'


class InputSchema(BaseModel):
    id: int = Field(..., description='模板id')


class DataSchema(BaseModel):
    title_list: Optional[List[Dict[str, Union[str, int]]]] = Field(None, description='报告名称')
    header: Dict[str, Union[str, int, float, None]] = Field(None, description='页眉')
    footer: Dict[str, Union[str, int, float, None]] = Field(None, description='页脚')
    header_position: Optional[str] = Field(None, description='页眉位置: 左边展示/居中展示/右边展示')
    footer_position: Optional[str] = Field(None, description='页脚位置: 左边展示/居中展示/右边展示')
    # 左中右页眉页脚（type: 0=关联title_mapping字段 1=自定义文本）
    left_header: Optional[Dict[str, Union[str, int, float, None]]] = Field(None, description='左页眉')
    mid_header: Optional[Dict[str, Union[str, int, float, None]]] = Field(None, description='中页眉')
    right_header: Optional[Dict[str, Union[str, int, float, None]]] = Field(None, description='右页眉')
    left_footer: Optional[Dict[str, Union[str, int, float, None]]] = Field(None, description='左页脚')
    mid_footer: Optional[Dict[str, Union[str, int, float, None]]] = Field(None, description='中页脚')
    right_footer: Optional[Dict[str, Union[str, int, float, None]]] = Field(None, description='右页脚')
    # 可选择关联的字段名列表（来自 title_mapping 的 name）
    title_mapping_name_list: List[str] = Field([], description='title_mapping 字段名列表')
    remark: Dict[str, Union[str, int, float, None]] = Field(None, description='备注')
    page_num_type: str = Field(..., description='页码类型')
    page_num_type_list: List[str] = Field(..., description='页码类型列表')
    header_type_list: List[str] = Field(..., description='页码类型列表')
    footer_type_list: List[str] = Field(..., description='页码类型列表')
    margin: Optional[Dict[str, Union[str, int, float, None]]] = Field(None, description='动态边距(mm)')
    orientation: Optional[Dict[str, Union[str, int, float, None]]] = Field(None, description='横向/纵向')
    line_height: Optional[Dict[str, Union[str, int, float, None]]] = Field(None, description='行边距')


class OutSchema(BaseModel):
    code: int = Field(0, description='状态码')
    message: str = Field('获取成功', description='返回信息')
    data: DataSchema = Field(..., description='返回数据')

@router.get('/get_template_extra_info', response_model=OutSchema)
@log_response
async def get_template_extra_info(template_id: int, measure_mode: Optional[int] = None):

    class_db_con = connections.get('classic_db')
    is_classic = measure_mode == MeasureMode.classic.value

    if is_classic:
        template_instance = await TemplateDoc.get_or_none(id=template_id, is_del=0).using_db(class_db_con)
    else:
        template_instance = await TemplateDoc.get_or_none(id=template_id)
    if not template_instance:
        raise APIException(ErrorCode.TEMPLATE_NOT_FOUND)

    header_and_footer_info: dict = {}

    if is_classic:
        # 经典模式（HTML 模板）：从配置文件的 extra_info 取值
        header_and_footer_info: dict = {}
    else:
        # 向导模式（HTML 模板）：从 .py 配置文件的 extra_info 取值（不再解析 DOCX）
        header_and_footer_info: dict = {}

    # 设置默认值
    if is_classic:
        header_and_footer_info.setdefault('page_num_type', TemplatePageNumType.no_page.decs)
    else:
        header_and_footer_info.setdefault('page_num_type', TemplatePageNumType.get_name_desc_by_value(0))
    header_and_footer_info.setdefault('header', {})
    header_and_footer_info.setdefault('footer', {})
    header_and_footer_info.setdefault('header_position', '居中展示')
    header_and_footer_info.setdefault('footer_position', '居中展示')
    header_and_footer_info.setdefault('remark', {})
    header_and_footer_info.setdefault('title_list', [])
    header_and_footer_info.setdefault('margin', {'value': '20'})
    header_and_footer_info.setdefault('orientation', {'value': 0})
    header_and_footer_info.setdefault('line_height', {'value': '1.5'})

    # 读取 Python 配置文件的 extra_info（经典/新模式通用）
    template_name = template_instance.name
    if is_classic:
        structure_module = config.classic_structure_module
    else:
        structure_module = config.structure_module

    try:
        from utils.template_utils import import_template_module
        private_mod = import_template_module(structure_module, template_name)
    except Exception as e:
        print(f"[get_template_extra_info] import {structure_module}.{template_name} failed: {e}")
        private_mod = None
    if private_mod and hasattr(private_mod, 'extra_info'):
        extra_info_config = getattr(private_mod, 'extra_info')
        # 备注
        if 'remark' in extra_info_config:
            header_and_footer_info['remark'] = extra_info_config['remark']
        # 动态边距
        if 'margin' in extra_info_config:
            header_and_footer_info['margin'] = extra_info_config['margin']
        # 横向/纵向
        if 'orientation' in extra_info_config:
            header_and_footer_info['orientation'] = extra_info_config['orientation']
        # 行边距
        if 'line_height' in extra_info_config:
            header_and_footer_info['line_height'] = extra_info_config['line_height']
        # 左中右页眉页脚（新格式）
        for _key in ['left_header', 'mid_header', 'right_header', 'left_footer', 'mid_footer', 'right_footer']:
            if _key in extra_info_config:
                header_and_footer_info[_key] = extra_info_config[_key]
        # 页码类型：经典模式从 page_num.position 映射，非经典从 page_num_type
        if is_classic:
            if 'page_num' in extra_info_config:
                pos = extra_info_config['page_num'].get('position', '')
                # 使用 TemplatePageNumType 常量映射 position 字符串 → value → desc
                _POS_TO_VALUE = {
                    'left': TemplatePageNumType.left_page.value,
                    'center': TemplatePageNumType.center_page.value,
                    'right': TemplatePageNumType.right_page.value,
                }
                value = _POS_TO_VALUE.get(pos)
                if value is not None:
                    header_and_footer_info['page_num_type'] = TemplatePageNumType.get_name_desc_by_value(value)
                else:
                    header_and_footer_info['page_num_type'] = TemplatePageNumType.no_page.decs

            # 页眉/页脚/标题 从配置文件取
            if 'header' in extra_info_config:
                header_and_footer_info['header'] = extra_info_config['header']
                # 同时以 TemplatePageNumType desc 格式暴露 position
                _pos = extra_info_config['header'].get('position', '')
                header_and_footer_info['header_position'] = _position_to_desc(_pos)
            if 'footer' in extra_info_config:
                header_and_footer_info['footer'] = extra_info_config['footer']
                _pos = extra_info_config['footer'].get('position', '')
                header_and_footer_info['footer_position'] = _position_to_desc(_pos)
            if 'title_list' in extra_info_config:
                header_and_footer_info['title_list'] = extra_info_config['title_list']
        else:
            if extra_info_config.get('page_num_type') is not None:
                header_and_footer_info['page_num_type'] = TemplatePageNumType.get_name_desc_by_value(
                    extra_info_config.get('page_num_type')
                )
            # 标题列表（向导 HTML 模板用 __title_list__）
            if 'title_list' in extra_info_config:
                header_and_footer_info['title_list'] = extra_info_config['title_list']

    # 读取 title_mapping 的所有 name，供前端选择关联字段
    title_mapping_name_list = []
    if private_mod and hasattr(private_mod, 'title_mapping'):
        _tm = getattr(private_mod, 'title_mapping')
        if isinstance(_tm, dict):
            for _t_key, _t_desc in _tm.items():
                if isinstance(_t_desc, dict) and _t_desc.get('name'):
                    title_mapping_name_list.append(_t_desc['name'])
    header_and_footer_info['title_mapping_name_list'] = title_mapping_name_list

    header_and_footer_info['page_num_type_list'] = [k for k, v in TemplatePageNumType.generate_decs_value_map().items()]
    header_and_footer_info['header_type_list'] = [k for k, v in TemplateFootAndHeaderType.generate_decs_value_map().items()]
    header_and_footer_info['footer_type_list'] = [k for k, v in TemplateFootAndHeaderType.generate_decs_value_map().items()]


    return {'code': 200, 'message': '获取页眉页脚标题成功', 'data': header_and_footer_info}