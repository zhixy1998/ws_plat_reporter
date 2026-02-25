
import os
from pathlib import Path
from tortoise import transactions

from tortoise import connections
from fastapi import APIRouter
from pydantic import BaseModel, Field
from utils.template_utils import validate_python_file

from ..model.template_doc import TemplateDoc
from exceptions.error import ErrorCode
from exceptions.command_exception import APIException
from utils.log_decorator import log_response
from constants.template_constant import MeasureMode
from config import config


router = APIRouter()

class InputSchema(BaseModel):
    template_id: int = Field(..., description='模板id')
    module_code: str = Field(..., description='模块代码')
    measure_mode: int = Field(..., description='测量模式：0经典 1向导')

@router.post('/save_template_private_code')
@log_response
async def save_template_private_code(data: InputSchema):

    class_db_con = connections.get('classic_db')
    if data.measure_mode == MeasureMode.classic.value:
        template = await TemplateDoc.get_or_none(id=data.template_id, is_del=0).using_db(class_db_con)
    else:
        template = await TemplateDoc.get_or_none(id=data.template_id)
    if not template:
        raise APIException(ErrorCode.TEMPLATE_NOT_FOUND)

    # 验证代码合法性
    is_valid, error_msg = await validate_python_file(data.module_code)
    if not is_valid:
        raise APIException(ErrorCode.TEMPLATE_PRIVATE_CODE_INVALID, f'私有代码验证失败: {error_msg}')

    if data.measure_mode == MeasureMode.classic.value:
        module_dir = config.classic_structure_path
    else:
        module_dir = config.structure_path
    module_dir.mkdir(parents=True, exist_ok=True)
    module_path = module_dir / f'{template.name}.py'

    try:
        # 保存代码到文件
        with open(module_path, 'w', encoding='utf-8') as f:
            f.write(data.module_code)
    except Exception as e:
        raise APIException(ErrorCode.SAVE_TEMPLATE_FAILED, f'保存私有代码失败: {str(e)}')
    
    if data.measure_mode == MeasureMode.classic.value:
        template_doc = await TemplateDoc.get_or_none(id=data.template_id).using_db(class_db_con)
    else:
        template_doc = await TemplateDoc.get_or_none(id=data.template_id)
    if template_doc:
        template_doc.python_config = data.module_code
        await template_doc.save()
        print(f"DEBUG: Python配置已存入数据库（复制模式），template_id={data.template_id}")

    return {'code': 200, 'message': '私有代码保存成功'}