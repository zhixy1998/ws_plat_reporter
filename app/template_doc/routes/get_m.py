
from typing import List, Optional
from fastapi import APIRouter, Query
from ..model.template_doc import TemplateDoc
from pydantic import BaseModel, Field
from exceptions.error import ErrorCode
from exceptions.command_exception import APIException
from utils.log_decorator import log_response
from utils.table_data_processor import GetHeaderAndData

router = APIRouter()

class InputSchema(BaseModel):
    task_id: str = Field(..., description='任务id')
    sample_id: str = Field(None, description='样品id')

@router.post('/get_m')
@log_response
async def get_m(data: InputSchema):
    get_header_and_data_class_instance = GetHeaderAndData(data.task_id)
    await get_header_and_data_class_instance._get_all_headers()
    all_m = await get_header_and_data_class_instance.get_all_m()
    return {'code': 200, 'message': 'success', 'data': all_m}