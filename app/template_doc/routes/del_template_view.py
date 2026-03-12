from typing import List, Optional
from fastapi import APIRouter, Query
from ..model.template_doc import TemplateDoc
from ..model.template_doc_base import TemplateDocBase
from pydantic import BaseModel, Field
from exceptions.error import ErrorCode
from exceptions.command_exception import APIException
from utils.log_decorator import log_response

router = APIRouter()

class InputSchema(BaseModel):
    id: int = Field(..., description='模板id')

@router.post('/del_template')
@log_response
async def del_template(data: InputSchema):
    template_instance = await TemplateDoc.get_or_none(id=data.id, is_del=0)
    if template_instance:
        await TemplateDocBase.filter(id=template_instance.base_template_id, is_del=0).update(is_del=1)
    await TemplateDoc.filter(id=data.id).update(is_del=1)
    return {'code': 200, 'message': '模板删除成功'}