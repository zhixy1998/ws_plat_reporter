import base64
from io import BytesIO

from fastapi import APIRouter
from tortoise import connections
from pydantic import BaseModel, Field
from fastapi.responses import StreamingResponse

from exceptions.error import ErrorCode
from app.db import execute_safe_sql_classic
from utils.log_decorator import log_response
from exceptions.command_exception import APIException
from utils.classic_fille_template_utils_simple import ClassicFillDataUtils
from utils.classic_html_builder import ClassicHtmlBuilder
from app.template_doc.model.template_doc import TemplateDoc


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
    """导出经典模式报告，从数据库取 HTML 模板，Playwright 渲染 PDF 下载"""
    classic_db_con = connections.get('classic_db')
    template_id = data.template_id
    task_id = data.task_id
    measure_type = await get_measure_type(task_id)

    if template_id is None:
        raise APIException(ErrorCode.TEMPLATE_NOT_FOUND)

    template = await TemplateDoc.get_or_none(id=template_id, using_db=classic_db_con)
    if not template:
        raise APIException(ErrorCode.TEMPLATE_NOT_FOUND)

    template_name = template.name
    html_template_str = _get_html_from_template(template)

    fill_data_instance = ClassicFillDataUtils(
        template_name, template_id=template_id, measure_type=measure_type
    )

    fill_data_instance.get_common_data_by_endpoint(task_id, data.analysis_id)
    if data.analysis_id and len(data.analysis_id.split(',')) == 1:
        fill_data_instance.single_sample = True
    fill_data_instance.end_point_header_and_data = (
        fill_data_instance.get_table_head_data_from_endpoint(
            task_id, data.analysis_id, data.all_display, data.digit
        )
    )

    contexts = await fill_data_instance.get_html_contexts(
        image_base64=data.image_base64
    )

    # 计算各区块是否有字段
    for _flag, _keys in [
        ('__has_instrument__',   ['仪器型号_t', '仪器序号_t', '光谱带宽_t', '激发狭缝_t', '发射狭缝_t', '激发滤光片_t', '发射滤光片_t', '灵敏度_t', '发射波长_t']),
        ('__has_file_info__',    ['数据文件_t', '分析时间_t', '数据类型_t', '方法名称_t']),
        ('__has_calibration__',  ['曲线方程_t', '方程次数_t', '公式_t', '校正方法_t', '自动切换样品池_t', '零点插入_t', '测量波长_t', '强制过零点_t', '扫描模式_t', '激发波长_t', '发射波长_t', '重复测量_t']),
        ('__has_spectrum_scan__',['扫描范围_t', '光度模式_t', '增益_t', '波长间隔_t', '扫描间隔_t', '扫描速度_t', '能量灯_t', '数据文件_t', '分析时间_t', '数据类型_t', '方法名称_t']),
        ('__has_time_scan__',    ['光度模式_t', '增益_t', '时间单位_t', '扫描时间_t', '时间间隔_t', '扫描速度_t', '能量灯_t', '采样数_t', '测量波长_t', '数据文件_t', '分析时间_t', '数据类型_t', '方法名称_t']),
        ('__has_analysis_record__',['分析员_t', '审核员_t', '备注_t', '注释_t']),
    ]:
        contexts[_flag] = any(contexts.get(k) for k in _keys)

    builder = ClassicHtmlBuilder(template_html=html_template_str)
    pdf_bytes = builder.build_pdf(contexts)

    if not pdf_bytes:
        raise APIException(ErrorCode.INTERNAL_ERROR, "PDF转换失败")

    from urllib.parse import quote
    filename = f"{template_name}_{task_id}.pdf"
    encoded_filename = quote(filename)

    return StreamingResponse(
        BytesIO(pdf_bytes),
        media_type="application/pdf",
        headers={
            "Content-Disposition": f"attachment; filename*=UTF-8''{encoded_filename}",
            "Content-Length": str(len(pdf_bytes)),
        }
    )


def _get_html_from_template(template) -> str:
    """从 TemplateDoc 记录中提取 HTML 模板字符串。"""
    content_b64 = template.template_content
    if not content_b64:
        return ''
    raw_bytes = base64.b64decode(content_b64)
    for enc in ('utf-8', 'gbk', 'gb2312', 'gb18030', 'latin-1'):
        try:
            return raw_bytes.decode(enc)
        except (UnicodeDecodeError, UnicodeError):
            continue
    print(f"[_get_html_from_template] 模板 {template.name}(id={template.id}) 无法解码，使用 utf-8 replace 兜底")
    return raw_bytes.decode('utf-8', errors='replace')


async def get_measure_type(task_id):
    sql = "select measure_type from f_t_measure_task where id = %s"
    sql_result = await execute_safe_sql_classic(sql, [task_id], return_dict=True)
    if sql_result:
        return sql_result[0].get('measure_type')
    return None
