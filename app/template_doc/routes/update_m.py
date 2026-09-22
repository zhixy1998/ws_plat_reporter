
import os
import re
from typing import List, Dict, Optional
from fastapi import APIRouter
from pydantic import BaseModel, Field

from config import config
from utils.log_decorator import log_response
from app.template_doc.model.template_doc import TemplateDoc
from utils.fille_template_utils import FillDataUtils
from utils.template_utils import import_template_module

router = APIRouter()

class InputSchema(BaseModel):
    template_id: int = Field(..., description='模板id')
    stand: List[str] = Field(..., description='标准头列表')
    unknown_map: Dict[str, str] = Field(..., description='未知头字典')
    exist_stand: Optional[Dict[str, str]] = Field(None, description='已存在的标准样映射 {identity: printTitle}')
    exist_unknown: Optional[Dict[str, str]] = Field(None, description='已存在的未知样映射 {identity: printTitle}')
    updateBy: Optional[str] = Field(None, description='更新人')
    deviceSerialNumber: Optional[str] = Field(None, description='设备序列号')

    model_config = {
        "extra": "ignore"
    }

@router.post('/update_m')
@log_response
async def update_m(data: InputSchema):
    template_id = data.template_id
    stand = data.stand
    unknown_map = data.unknown_map
    exist_unknown = data.exist_unknown or {}
    
    # 获取模板信息
    template = await TemplateDoc.get_or_none(id=template_id)
    if not template:
        return {'code': 400, 'message': '模板不存在'}
    
    # 获取当前的 HEADER_M_MAPPING_LIST 和 STAND
    current_header_mapping = []
    current_stand = []
    current_table_header_map = {}
    try:
        fill_data_utils = FillDataUtils(template.name, template=template, fake=True)
        handler_instance = getattr(fill_data_utils.table_data_processor, 'handler_instance', None)
        if handler_instance:
            current_header_mapping = getattr(handler_instance, 'HEADER_M_MAPPING_LIST', [])
            current_stand = getattr(handler_instance, 'STAND', [])
            current_table_header_map = getattr(handler_instance, 'TABLE_HEADER_MAP', {}) or {}
    except Exception as e:
        print(f"读取当前模板配置失败（忽略并继续更新）: {e}")
    
    # 构建模板文件路径
    template_file_path = config.structure_path / f'{template.name}.py'
    
    if not os.path.exists(template_file_path):
        if template.python_config:
            with open(template_file_path, 'w', encoding='utf-8') as f:
                f.write(template.python_config)
        else:
            return {'code': 400, 'message': f'模板文件不存在: {template_file_path}'}
    
    # 读取模板文件内容
    with open(template_file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 1. 替换 STAND
    stand_pattern = r'(STAND\s*=\s*)\[.*?\]'
    stand_replacement = f'STAND = {repr(stand)}'
    content = re.sub(stand_pattern, stand_replacement, content, flags=re.DOTALL)
    
    # 2. 替换 HEADER_M_MAPPING_LIST
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

    # 3. 同步替换 TABLE_HEADER_MAP（保证新增的列如 t7_h 存在，且映射为正确的中文表头名）
    thm_pattern = r'(TABLE_HEADER_MAP\s*=\s*)\{.*?\}'
    old_mapping = current_header_mapping[0] if current_header_mapping else {}
    new_thm = {}
    for key, value in unknown_map.items():
        h_key = f'{key}_h'
        old_identity = old_mapping.get(key)
        existing_title = current_table_header_map.get(h_key)

        # 判断表头名称取值：
        # - 新增的列（不在旧映射中）
        # - 或更换了列标识（value != old_identity）
        # - 或旧表头名称本身就是原始英文标识（如 'sampleName'）
        # - 或尚未配置表头名称：
        # 优先使用 exist_unknown 中传过来的中文 printTitle
        if key not in old_mapping or value != old_identity or existing_title == value or not existing_title:
            title = exist_unknown.get(value) or existing_title or value
        else:
            title = existing_title

        new_thm[h_key] = title

    formatted_thm = '{\n'
    for k, v in new_thm.items():
        formatted_thm += f'        "{k}": "{v}",\n'
    formatted_thm = formatted_thm.rstrip(',\n') + '\n    }'

    if re.search(thm_pattern, content, flags=re.DOTALL):
        thm_replacement = f'TABLE_HEADER_MAP = {formatted_thm}'
        content = re.sub(thm_pattern, thm_replacement, content, flags=re.DOTALL)
    else:
        # 如果类中暂未声明 TABLE_HEADER_MAP，追加到 TableDataHandler 内部
        thm_definition = f'\n    TABLE_HEADER_MAP = {formatted_thm}\n'
        content = re.sub(r'(class TableDataHandler\(.*?\):)', rf'\1{thm_definition}', content)

    # 4. 同步更新 python_template_var（若存在，保证新增的 t_h 变量在模板变量字典中）
    ptv_match = re.search(r'python_template_var\s*=\s*(\{.*?\})', content, flags=re.DOTALL)
    if ptv_match:
        ptv_body = ptv_match.group(1)
        additions = []
        for key in unknown_map.keys():
            h_key = f'{key}_h'
            if f'"{h_key}"' not in ptv_body and f"'{h_key}'" not in ptv_body:
                additions.append(f'    "{h_key}": {{"fill_type": 0}},')
        if additions:
            addition_str = '\n' + '\n'.join(additions)
            content = re.sub(
                r'(python_template_var\s*=\s*\{)',
                rf'\1{addition_str}',
                content,
                count=1
            )
    
    # 5. 写回文件
    with open(template_file_path, 'w', encoding='utf-8') as f:
        f.write(content)

    # 6. 同步更新数据库字段
    template.python_config = content
    await template.save()

    # 7. 重新加载模块缓存
    try:
        import_template_module(config.structure_module, template.name, reload=True)
    except Exception as e:
        print(f"重新加载模板模块失败: {e}")
    
    return {
        'code': 200, 
        'message': '更新成功', 
        'data': {
            'template_file': str(template_file_path),
            'old_stand': current_stand,
            'new_stand': stand,
            'old_header_mapping': current_header_mapping,
            'new_header_mapping': header_mapping_list
        }
    }