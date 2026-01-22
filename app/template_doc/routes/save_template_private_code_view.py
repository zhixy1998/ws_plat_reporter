
import os
from pathlib import Path
from tortoise import transactions

from fastapi import APIRouter
from pydantic import BaseModel, Field
from utils.template_utils import validate_python_file

from ..model.template_doc import TemplateDoc
from exceptions.error import ErrorCode
from exceptions.command_exception import APIException
from utils.log_decorator import log_response


router = APIRouter()

class InputSchema(BaseModel):
    template_id: int = Field(..., description='模板id')
    module_code: str = Field(..., description='模块代码')

@router.post('/save_template_private_code')
@log_response
async def save_template_private_code(data: InputSchema):
    template = await TemplateDoc.get_or_none(id=data.template_id)
    if not template:
        raise APIException(ErrorCode.TEMPLATE_NOT_FOUND)

    # 验证代码合法性
    is_valid, error_msg = await validate_python_file(data.module_code)
    if not is_valid:
        raise APIException(ErrorCode.TEMPLATE_PRIVATE_CODE_INVALID, f'私有代码验证失败: {error_msg}')

    module_dir = Path(__file__).parent.parent.parent.parent / 'template_structure'
    module_dir.mkdir(exist_ok=True)
    module_path = module_dir / f'{template.name}.py'

    try:
        # 保存代码到文件
        with open(module_path, 'w', encoding='utf-8') as f:
            f.write(data.module_code)
    except Exception as e:
        raise APIException(ErrorCode.SAVE_TEMPLATE_FAILED, f'保存私有代码失败: {str(e)}')
    
    template_doc = await TemplateDoc.get_or_none(id=data.template_id)
    if template_doc:
        template_doc.python_config = data.module_code
        await template_doc.save()
        print(f"DEBUG: Python配置已存入数据库（复制模式），template_id={data.template_id}")

    return {'code': 200, 'message': '私有代码保存成功'}