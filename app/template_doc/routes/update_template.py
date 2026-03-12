import importlib
import os
from pathlib import Path
from tortoise import transactions

from fastapi import APIRouter
from pydantic import BaseModel, Field
from tortoise import connections

from ..model.template_doc import TemplateDoc
from exceptions.error import ErrorCode
from exceptions.command_exception import APIException
from utils.log_decorator import log_response
from constants.template_constant import MeasureMode
from config import config


router = APIRouter()

class InputSchema(BaseModel):
    id: int = Field(..., description='模板id')
    name: str = Field(None, description='模板名称')
    measure_mode: int = Field(None, description='测量模式')

@router.post('/update_template')
@log_response
async def update_template(data: InputSchema):
    if not data.name:
        return {'code': 200, 'message': '模板名称未更改'}

    if data.measure_mode == MeasureMode.classic.value:
        class_db_con = connections.get('classic_db')
        template = await TemplateDoc.get_or_none(id=data.id).using_db(class_db_con)
    else:
        template = await TemplateDoc.get_or_none(id=data.id)
    if not template:
        raise APIException(ErrorCode.TEMPLATE_NOT_FOUND)

    old_name = template.name
    new_name = data.name

    if old_name == new_name:
        return {'code': 200, 'message': '模板名称未更改'}

    if data.measure_mode == MeasureMode.classic.value:
        template_dir = config.classic_structure_path
    else:
        template_dir = config.structure_path
    # project_root = Path(__file__).resolve().parent.parent.parent.parent
    # template_dir = project_root / config.TEMPLATE_STRUCTURE_DIR

    old_file_path = template_dir / f"{old_name}.py"
    new_file_path = template_dir / f"{new_name}.py"

    if not os.path.exists(old_file_path):
        raise APIException(ErrorCode.TEMPLATE_FILE_NOT_FOUND)

    if os.path.exists(new_file_path):
        raise APIException(ErrorCode.TEMPLATE_FILE_ALREADY_EXISTS)

    try:
        async with transactions.in_transaction('default'):
            os.rename(old_file_path, new_file_path)

            template.name = new_name
            await template.save()

    except Exception as e:
        if os.path.exists(new_file_path) and not os.path.exists(old_file_path):
            os.rename(new_file_path, old_file_path)
        raise APIException(ErrorCode.TEMPLATE_UPDATE_FAILED, detail=str(e))

    return {'code': 200, 'message': '模板更新成功'}