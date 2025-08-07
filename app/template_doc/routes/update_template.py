from typing import List, Optional
from fastapi import APIRouter, Query
from ..model.template_doc import TemplateDoc
from pydantic import BaseModel, Field
from exceptions.error import ErrorCode
from exceptions.command_exception import APIException
from utils.log_decorator import log_response

router = APIRouter()

class InputSchema(BaseModel):
    id: int = Field(..., description='模板id')
    name: str = Field(None, description='模板名称')

@router.post('/update_template')
@log_response
async def update_template(data: InputSchema):
    template = await TemplateDoc.get_or_none(id=data.id)
    if not template:
        raise APIException(ErrorCode.TEMPLATE_NOT_FOUND)
    template.name = data.name
    await template.save()
    return {'code': 200, 'message': '模板更新成功'}