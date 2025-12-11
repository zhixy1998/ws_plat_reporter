from io import BytesIO

from fastapi import APIRouter
from tortoise import connections
from pydantic import BaseModel, Field
from fastapi.responses import StreamingResponse

from exceptions.error import ErrorCode
from utils.log_decorator import log_response
from exceptions.command_exception import APIException
from utils.template_utils import get_doc_name_and_doc_stream_obj
from utils.classic_fille_template_utils_simple import ClassicFillDataUtils
from .classic_export_original_data_doc_view import get_measure_type
from utils.template_utils import convert_docx_to_pdf_base64, convert_docx_to_pdf_bytes

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

@router.post('/preview_template')
@log_response
async def preview_template(data: InputSchema):
    """预览模板，将docx转换为PDF的base64返回"""
    classic_db_con = connections.get('classic_db')
    template_id = data.template_id
    task_id = data.task_id
    sample_id = data.sample_id
    serial_number = data.serial_number

    # 直接获取文件流，更简单
    measure_type = await get_measure_type(task_id)
    if template_id is None:
        raise APIException(ErrorCode.TEMPLATE_NOT_FOUND)
    original_template_name, original_doc_stream_obj = await get_doc_name_and_doc_stream_obj(template_id=template_id, conn=classic_db_con)
    fill_data_instance_original = ClassicFillDataUtils(original_template_name, template_id=template_id, measure_type=measure_type)
    try:
        original_doc_stream_obj = await fill_data_instance_original.fill_data(doc_stream=original_doc_stream_obj, task_id=task_id, sample_id=sample_id, 
            serial_number=serial_number, image_base64=data.image_base64, analysis_id=data.analysis_id, all_display=data.all_display, 
            is_repeat_mode=data.is_repeat_mode, digit=data.digit)
        if original_doc_stream_obj:
            # 转换为PDF
            pdf_base64 = convert_docx_to_pdf_base64(original_doc_stream_obj)
    
            return {
                'code': 200,
                'message': '预览成功',
                'data': {'pdf': pdf_base64}
            }
        return {
            'code': 200,
            'message': '预览成功',
            'data': {'pdf': ''}
        }
    except Exception as e:
        return {
            'code': 200,
            'message': '预览成功',
            'data': {'pdf': ''}
        }


@router.post('/preview_template_download')
async def preview_template_download(data: InputSchema):
    """
    预览模板，将docx转换为PDF并直接返回文件下载（调试用）
    """
    classic_db_con = connections.get('classic_db')
    template_id = data.template_id
    task_id = data.task_id
    sample_id = data.sample_id
    serial_number = data.serial_number

    # 直接获取文件流，更简单
    measure_type = await get_measure_type(task_id)
    if template_id is None:
        raise APIException(ErrorCode.TEMPLATE_NOT_FOUND)
    original_template_name, original_doc_stream_obj = await get_doc_name_and_doc_stream_obj(template_id=template_id, conn=classic_db_con)
    fill_data_instance_original = ClassicFillDataUtils(original_template_name, template_id=template_id, measure_type=measure_type)
    original_doc_stream_obj = await fill_data_instance_original.fill_data(doc_stream=original_doc_stream_obj, task_id=task_id, sample_id=sample_id, 
                             serial_number=serial_number, image_base64=data.image_base64, analysis_id=data.analysis_id, all_display=data.all_display, 
                             is_repeat_mode=data.is_repeat_mode, digit=data.digit)
    
    # 转换为PDF（返回字节流）
    pdf_bytes = convert_docx_to_pdf_bytes(original_doc_stream_obj)
    
    if not pdf_bytes:
        raise APIException(ErrorCode.DOCX_CONVERSION_FAILED, "PDF转换失败")
    
    # 生成文件名（处理中文编码）
    from urllib.parse import quote
    filename = f"{original_template_name}_{task_id}.pdf"
    encoded_filename = quote(filename)
    
    # 返回文件下载
    return StreamingResponse(
        BytesIO(pdf_bytes),
        media_type="application/pdf",
        headers={
            "Content-Disposition": f"attachment; filename*=UTF-8''{encoded_filename}"
        }
    )