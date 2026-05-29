import io
from fastapi import Request
from typing import List

from pydantic import BaseModel, Field
from fastapi.responses import StreamingResponse
from fastapi import APIRouter, UploadFile, File

from app.db import execute_safe_sql
from exceptions.error import ErrorCode
from exceptions.command_exception import APIException
from app.admin_backup.utils.data_operation import DataOperation
from app.admin_backup.utils.encrypt import encrypt_json, decrypt_json

router = APIRouter()

class InputSchema(BaseModel):
    ids: List[str] = Field(..., description='方法id列表')
    operation_type: str = Field(..., description='类型 method: 方法, task: 任务')

@router.post('/guide_export')
async def guide_export(data: InputSchema):
    ids = data.ids
    result_json = {}
    if not ids:
        return StreamingResponse(
            io.BytesIO(encrypt_json({})),
            media_type="application/octet-stream",
            headers={
                "Content-Disposition": "attachment" 
            }
        )

    if data.operation_type == 'method':
        result_json['method_data'] = {
            't_measure_method': await DataOperation.static_method_get_measure_method_info(
                ids,
                table_prefix='t_',
                sql_executor=execute_safe_sql,
            )
        }
    if data.operation_type == 'task':
        task_data = {}
        for task_id in ids:
            task_id_map = {}
            data_operation = DataOperation(task_id)
            task_id_map['t_measure_task'] = await data_operation.get_measure_task_info(
                table_prefix='t_',
                sql_executor=execute_safe_sql,
            )
            task_id_map['t_measure_analysis_data'] = await data_operation.get_measure_analysis_data_info(
                table_prefix='t_',
                sql_executor=execute_safe_sql,
            )
            task_id_map['t_measure_data'] = await data_operation.get_measure_data_info(
                table_prefix='t_',
                sql_executor=execute_safe_sql,
            )
            task_id_map['t_measure_method'] = await data_operation.get_measure_method_info(
                table_prefix='t_',
                sql_executor=execute_safe_sql,
            )
            task_id_map['t_measure_sample'] = await data_operation.get_measure_sample_info(
                table_prefix='t_',
                sql_executor=execute_safe_sql,
            )
            task_id_map['t_measure_task_attachment'] = await data_operation.get_measure_task_attachment_info(
                table_prefix='t_',
                sql_executor=execute_safe_sql,
            )
            task_id_map['t_measure_project'] = await data_operation.get_measure_project_info(
                table_prefix='t_',
                sql_executor=execute_safe_sql,
            )
            task_data[task_id] = task_id_map
        result_json['task_data'] = task_data
    
    encrypt_end_bytes = encrypt_json(result_json)
    return StreamingResponse(
        io.BytesIO(encrypt_end_bytes),
        media_type="application/octet-stream",   # 强制下载
        headers={
            "Content-Disposition": "attachment" 
        }
    )

    
"""
经典模式下的任务包叫 .UVCD 方法包叫 .UVCM     向导模式下的任务包叫 .UVGD  方法包叫 .UVGM
"""
@router.post('/guide_import')
async def guide_import(
    request: Request,
    file: UploadFile = File(...,  description='备份文件'),
    ):
    content_bytes = await file.read()
    file_name = file.filename
    if file_name.split('.')[1] not in ['uvgm', 'uvgd']:
        raise APIException(ErrorCode.INVALID_FILE_FORMAT)
    content_str = content_bytes.decode('utf-8')
    decrypt_data = decrypt_json(content_str)
    try:
        result = await DataOperation.insert_data_guide(decrypt_data)
        if result:
            return {'code': 200}
    except Exception as e:
        raise APIException(ErrorCode.IMPORT_ERROR, str(e))
