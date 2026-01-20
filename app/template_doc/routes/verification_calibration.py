import requests
from typing import Dict, Any
from fastapi import APIRouter
from pydantic import BaseModel, Field


from config import config
from utils.log_decorator import log_response
from utils.verification_calibration_utils.verification_calibration_handle import InspectionAndCorrectionReport

router = APIRouter()


class VerificationCalibrationInputSchema(BaseModel):
    """验证校准请求数据模型"""
    task_id: str = Field(..., description='任务id')
    sample_id: Dict[str, Any] = Field(None, description='样品id')


@router.post('/verification_calibration')
@log_response
async def verification_calibration(data: VerificationCalibrationInputSchema):
    """
    验证校准接口
    
    Args:
        data: 包含校准ID和验证数据的请求体
        
    Returns:
        JSON响应，包含code和message
    """
    try:
        task_id = data.task_id
        sample_id = data.sample_id

        verification_calibration_url = config.verification_calibration_url
        request_url  = verification_calibration_url + f'?taskId={task_id}'
        res = requests.get(request_url)
        res_json = res.json()

        iar = InspectionAndCorrectionReport(vc_data_list=res_json.get('data').get('worksheets'))
        iar.run()
        print("Verification Calibration Response:", res_json.get('data').get('worksheets'))

        
        
        return {
            'code': 200,
            'message': '验证校准成功',
            'data': {
            }
        }
    except Exception as e:
        return {
            'code': 500,
            'message': f'验证校准失败: {str(e)}'
        }
