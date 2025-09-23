
import requests
import os, urllib
from fastapi import APIRouter
from pydantic import BaseModel, Field
from utils.log_decorator import log_response

router = APIRouter()

class InputSchema(BaseModel):
    task_id: str = Field(..., description='任务id')
    sample_id: str = Field(None, description='样品id')

@router.post('/get_m')
@log_response
async def get_m(data: InputSchema):
    task_id = data.task_id
    sample_id = data.sample_id
    template_common_url = os.getenv('TEMPLATE_TABLE_HEAD_DATA_URL') + '?taskId=' + urllib.parse.quote(str(task_id), safe='') + '&sampleId=' + urllib.parse.quote(str(sample_id), safe='')
    response = requests.get(template_common_url)
    res_json = response.json()
    # print(res_json)
    return {'code':200, 'message':'success', 'data':res_json.get('data')}