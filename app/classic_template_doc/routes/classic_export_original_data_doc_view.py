import io
from io import BytesIO

from fastapi import APIRouter
from tortoise import connections
from pydantic import BaseModel, Field
from fastapi.responses import StreamingResponse

from exceptions.error import ErrorCode
from app.db import execute_safe_sql_classic
from utils.log_decorator import log_response
from exceptions.command_exception import APIException
from utils.template_utils import get_doc_name_and_doc_stream_obj
from utils.classic_fille_template_utils_simple import ClassicFillDataUtils
from utils.template_utils import convert_docx_to_pdf_bytes


router = APIRouter()

class InputSchema(BaseModel):
    template_id: int = Field(..., description='模板id')
    task_id: str = Field(..., description='任务id')
    sample_id: str = Field(None, description='样品id')
    analysis_id: str = Field(None, description='分析id')
    all_display: int = Field(0, description='Abs和T%是否显示')
    serial_number: str = Field(None, description='样品序号')
    is_repeat_mode: int = Field(0, description='是否重复模式')
    digit: int = Field(None, description='保留小数位数')
    image_base64: str = Field(None, description='图片base64')

class OutSchema(BaseModel):
    pass

@router.post('/classic_export_original_report_docx')
@log_response
async def export_docx(data: InputSchema):
    # print(f"[DEBUG export_docx] ===== 开始处理请求 =====")
    # print(f"[DEBUG export_docx] task_id={data.task_id}, template_id={data.template_id}")
    classic_db_con = connections.get('classic_db')
    template_id = data.template_id
    task_id = data.task_id
    sample_id = data.sample_id
    serial_number = data.serial_number
    measure_type = await get_measure_type(task_id)
    # print(f"[DEBUG export_docx] measure_type={measure_type}")
    if template_id is None:
        raise APIException(ErrorCode.TEMPLATE_NOT_FOUND)
    original_template_name, original_doc_stream_obj = await get_doc_name_and_doc_stream_obj(template_id=template_id, conn=classic_db_con)
    # print(f"[DEBUG export_docx] template_name={original_template_name}, doc_stream type={type(original_doc_stream_obj)}")
    fill_data_instance_original = ClassicFillDataUtils(original_template_name, template_id=template_id, measure_type=measure_type)
    original_doc_stream_obj = await fill_data_instance_original.fill_data(doc_stream=original_doc_stream_obj, task_id=task_id, sample_id=sample_id, 
                                serial_number=serial_number, image_base64=data.image_base64, analysis_id=data.analysis_id, all_display=data.all_display, 
                                is_repeat_mode=data.is_repeat_mode, digit=data.digit)
    # print(f"[DEBUG export_docx] fill_data 返回: type={type(original_doc_stream_obj)}, value={original_doc_stream_obj}")
    if original_doc_stream_obj:
        # 检查 docx 流大小
        pos_before = original_doc_stream_obj.tell()
        original_doc_stream_obj.seek(0, 2)  # 跳到末尾
        docx_size = original_doc_stream_obj.tell()
        original_doc_stream_obj.seek(0)      # 复位
        # print(f"[DEBUG export_docx] docx 流大小={docx_size} bytes, 位置恢复到0")

        pdf_bytes = convert_docx_to_pdf_bytes(original_doc_stream_obj)
        # print(f"[DEBUG export_docx] pdf_bytes 大小={len(pdf_bytes) if pdf_bytes else 0} bytes")
        # print(f"[DEBUG export_docx] pdf_bytes 前8字节={pdf_bytes[:8] if pdf_bytes else b''}")
    
        if not pdf_bytes:
            # print(f"[DEBUG export_docx] !! pdf_bytes 为空，抛出异常")
            raise APIException(ErrorCode.INTERNAL_ERROR, "PDF转换失败")
    
        # 生成文件名（处理中文编码）
        from urllib.parse import quote
        filename = f"{original_template_name}_{task_id}.pdf"
        encoded_filename = quote(filename)
        # print(f"[DEBUG export_docx] 准备返回 StreamingResponse, filename={filename}, pdf_size={len(pdf_bytes)}")
    
        # 返回文件下载
        return StreamingResponse(
            BytesIO(pdf_bytes),
            media_type="application/pdf",
            headers={
                "Content-Disposition": f"attachment; filename*=UTF-8''{encoded_filename}",
                "Content-Length": str(len(pdf_bytes)),
            }
        )
    else:
        # print(f"[DEBUG export_docx] !! fill_data 返回 None/False，返回空 PDF")
        empty_stream = io.BytesIO(b'')
        return StreamingResponse(
            empty_stream, 
            media_type="application/pdf", 
            headers={
                "Content-Disposition": "attachment; filename=original.pdf",
                "Content-Length": "0" 
            }
        )


async def get_measure_type(task_id):
    sql = "select measure_type from f_t_measure_task where id = %s"
    sql_result = await execute_safe_sql_classic(sql, [task_id], return_dict=True)
    if sql_result:
        return sql_result[0].get('measure_type')
    return None
