import io
from typing import List

from pydantic import BaseModel, Field
from fastapi.responses import StreamingResponse
from fastapi import APIRouter, UploadFile, File, Form

from exceptions.error import ErrorCode
from exceptions.command_exception import APIException
from app.admin_backup.utils.data_operation import DataOperation
from app.admin_backup.utils.encrypt import encrypt_json, decrypt_json
# from ..model.backup_model import FTMeasureAnalysisDatum, FTMeasureAnalysisImage, \
#     FTMeasureTaskAttachment, FTMeasureTask, FTMeasureDatum, FTMeasureEqualSample, FTMeasureMethod, \
#     FTMeasureSample, FTMeasureSampleHead


router = APIRouter()

class ExportInputModel(BaseModel):
    task_ids: List[str] = Field(None, description='任务id列表')
    method_keys: List[str] = Field(None, description='方法id列表')

@router.post('/export')
async def backup_export(data: ExportInputModel):
    task_ids = data.task_ids
    result_json = {}
    if task_ids:
        task_data = {}
        for task_id in task_ids:
            task_id_map = {}
            data_operation = DataOperation(task_id)
            task_id_map['f_t_measure_task'] = await data_operation.get_measure_task_info()
            task_id_map['f_t_measure_analysis_data'] = await data_operation.get_measure_analysis_data_info() # 分析数据表
            task_id_map['f_t_measure_data'] = await data_operation.get_measure_data_info() # 测量数据表
            task_id_map['f_t_measure_method'] = await data_operation.get_measure_method_info() # 测量方法表
            task_id_map['f_t_measure_sample'] = await data_operation.get_measure_sample_info() # 样品信息表
            task_id_map['f_t_measure_task_attachment'] = await data_operation.get_measure_task_attachment_info()

            task_data[task_id] = task_id_map
        result_json['task_data'] = task_data
    if data.method_keys:
        result_json['method_data'] = {'f_t_measure_method': await DataOperation.static_method_get_measure_method_info(data.method_keys) } # 测量方法表

    
    encrypt_end_bytes = encrypt_json(result_json)
    return StreamingResponse(
        io.BytesIO(encrypt_end_bytes),
        media_type="application/octet-stream",   # 强制下载
        headers={
            "Content-Disposition": "attachment" 
        }
    )



@router.post('/import')
async def backup_import(
    file: UploadFile = File(...,  description='备份文件')
    ):
    content_bytes = await file.read()
    file_name = file.filename
    if file_name.split('.')[1] not in ['nxd', 'nxm']:
        raise APIException(ErrorCode.INVALID_FILE_FORMAT)
    content_str = content_bytes.decode('utf-8')
    decrypt_data = decrypt_json(content_str)
    try:
        result = await DataOperation.insert_data(decrypt_data)
        if result:
            return {'code': 200}
    except Exception as e:
        raise APIException(ErrorCode.IMPORT_ERROR, str(e))