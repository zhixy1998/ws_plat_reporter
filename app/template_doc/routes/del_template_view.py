from typing import List, Optional
from fastapi import APIRouter, Query
from ..model.template_doc import TemplateDoc
from pydantic import BaseModel, Field
from exceptions.error import ErrorCode
from exceptions.command_exception import APIException

router = APIRouter()

class InputSchema(BaseModel):
    id: int = Field(..., description='模板id')

@router.post('/del_template')
async def del_template(data: InputSchema):
    await TemplateDoc.filter(id=data.id).update(is_del=1)
    return {'code': 200, 'message': '模删除成功'}