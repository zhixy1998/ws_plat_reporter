import io
from fastapi import Request
from typing import List

from pydantic import BaseModel, Field
from fastapi.responses import StreamingResponse
from fastapi import APIRouter, UploadFile, File, Form

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

    placeholders = ','.join(['%s'] * len(ids))

    if data.operation_type == 'method':
        sql_text = f"""
        select * from t_measure_method where id in ({placeholders})
        """
        method_data = await execute_safe_sql(sql_text, ids, return_dict=True)
        result_json['method_data'] = method_data
    if data.operation_type == 'task':
        sql_text = f"""
        select * from t_measure_task where id in ({placeholders})
        """
        task_data = await execute_safe_sql(sql_text, ids, return_dict=True)
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
