
from fastapi import APIRouter
from pydantic import BaseModel, Field
from fastapi.responses import StreamingResponse

from tortoise import connections

from exceptions.error import ErrorCode
from app.db import execute_safe_sql_classic
from utils.log_decorator import log_response
from constants.template_constant import MeasureType
from exceptions.command_exception import APIException
from app.template_doc.model.template_doc import TemplateDoc
from utils.template_utils import get_doc_name_and_doc_stream_obj
from utils.classic_fille_template_utils_simple import ClassicFillDataUtils

router = APIRouter()

class InputSchema(BaseModel):
    task_id: str = Field(..., description='任务id')
    sample_id: str = Field(None, description='样品id')
    serial_number: str = Field(None, description='样品序号')

class OutSchema(BaseModel):
    pass

@router.post('/classic_export_original_report_docx')
@log_response
async def export_docx(data: InputSchema):
    class_db_con = connections.get('classic_db')
    task_id = data.task_id
    sample_id = data.sample_id
    serial_number = data.serial_number
    print(f"task_id: {task_id}", f"sample_id: {sample_id}", f"serial_number: {serial_number}")
    measure_type = await get_measure_type(task_id)
    template_id = await get_template_id_by_measure_type(measure_type)
    if template_id is None:
        raise APIException(ErrorCode.TEMPLATE_NOT_FOUND)
    original_template_name, original_doc_stream_obj = await get_doc_name_and_doc_stream_obj(template_id=template_id, conn=class_db_con)
    fill_data_instance_original = ClassicFillDataUtils(original_template_name, template_id=template_id, measure_type=measure_type)
    original_doc_stream_obj = await fill_data_instance_original.fill_data(doc_stream=original_doc_stream_obj, task_id=task_id, sample_id=sample_id, serial_number=serial_number)
    # original_doc_stream_obj.seek(0)
    return StreamingResponse(original_doc_stream_obj, media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document", headers={
        "Content-Disposition": "attachment; filename=original.docx"
    })


async def get_measure_type(task_id):
    sql = "select measure_type from f_t_measure_task where id = %s"
    sql_result = await execute_safe_sql_classic(sql, [task_id], return_dict=True)
    if sql_result:
        return sql_result[0].get('measure_type')
    return None

async def get_template_id_by_measure_type(measure_type):
    class_db_con = connections.get('classic_db')
    template_id = None
    # 光谱扫描
    try:
        if measure_type == MeasureType.spectral_scanning.decs:
            template = await TemplateDoc.get_or_none(name='光谱原始数据', is_del=0, using_db=class_db_con)
            template_id = template.id
        # 时间扫描
        if measure_type == MeasureType.time_scanning.decs:
            template = await TemplateDoc.get_or_none(name='时间扫描原始数据', is_del=0, using_db=class_db_con)
            template_id = template.id
        # 定量测定
        if measure_type == MeasureType.quantitative_determination.decs:
            template = await TemplateDoc.get_or_none(name='定量原始数据', is_del=0, using_db=class_db_con)
            template_id = template.id
        # 光度测量
        if measure_type == MeasureType.photometric_measurement.decs:
            template = await TemplateDoc.get_or_none(name='光度原始数据', is_del=0, using_db=class_db_con)
            template_id = template.id
    except Exception as e:
        return
    return template_id if template_id else None
    