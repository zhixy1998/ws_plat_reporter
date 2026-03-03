
import importlib
import requests
import os, urllib
import re
import ast
from typing import List, Dict
from fastapi import APIRouter
from pydantic import BaseModel, Field
from utils.log_decorator import log_response
from config import config
from app.template_doc.model.template_doc import TemplateDoc
from utils.fille_template_utils import FillDataUtils
from constants.template_constant import ExperimentType

router = APIRouter()

class InputSchema(BaseModel):
    template_id: int = Field(..., description='模板id')
    stand: List[str] = Field(..., description='标准头列表')
    unknown_map: Dict[str, str] = Field(..., description='未知头字典')

@router.post('/update_m')
@log_response
async def update_m(data: InputSchema):
    template_id = data.template_id
    stand = data.stand
    unknown_map = data.unknown_map
    
    # 获取模板信息
    template = await TemplateDoc.get_or_none(id=template_id)
    if not template:
        return {'code': 400, 'message': '模板不存在'}
    
    # 获取当前的 HEADER_M_MAPPING_LIST 和 STAND
    fill_data_utils = FillDataUtils(template.name, template=template, fake=True)
    current_header_mapping = fill_data_utils.table_data_processor.handler_instance.HEADER_M_MAPPING_LIST
    current_stand = fill_data_utils.table_data_processor.handler_instance.STAND
    
    # 验证 unknown_map 的 key 是否与 HEADER_M_MAPPING_LIST 的 key 一致
    if current_header_mapping:
        # 假设只处理第一个映射表
        current_keys = set(current_header_mapping[0].keys())
        new_keys = set(unknown_map.keys())
        
        if current_keys != new_keys:
            return {
                'code': 400, 
                'message': f'unknown_map 的 key 与模板不一致。当前模板 keys: {current_keys}, 传入 keys: {new_keys}'
            }
    
    # 构建模板文件路径
    template_file_path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))),
        'template_structure',
        f'{template.name}.py'
    )
    
    if not os.path.exists(template_file_path):
        return {'code': 400, 'message': f'模板文件不存在: {template_file_path}'}
    
    # 读取模板文件内容
    with open(template_file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 替换 STAND
    stand_pattern = r'(STAND\s*=\s*)\[.*?\]'
    stand_replacement = f'STAND = {repr(stand)}'
    content = re.sub(stand_pattern, stand_replacement, content, flags=re.DOTALL)
    
    # 替换 HEADER_M_MAPPING_LIST
    # 将 unknown_map 转换为列表格式（保持与原格式一致）
    header_mapping_list = [unknown_map]
    header_pattern = r'(HEADER_M_MAPPING_LIST\s*=\s*)\[.*?\]'
    
    # 格式化字典输出，使其更美观
    formatted_dict = '{\n'
    for key, value in unknown_map.items():
        formatted_dict += f'        "{key}": "{value}",\n'
    formatted_dict = formatted_dict.rstrip(',\n') + '\n    }'
    
    header_replacement = f'HEADER_M_MAPPING_LIST = [{formatted_dict}]'
    content = re.sub(header_pattern, header_replacement, content, flags=re.DOTALL)
    
    # 写回文件
    with open(template_file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    return {
        'code': 200, 
        'message': '更新成功', 
        'data': {
            'template_file': template_file_path,
            'old_stand': current_stand,
            'new_stand': stand,
            'old_header_mapping': current_header_mapping,
            'new_header_mapping': header_mapping_list
        }
    }