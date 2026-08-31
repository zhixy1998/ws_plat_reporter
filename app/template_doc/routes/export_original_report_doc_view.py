"""
传入原始数据的模板id
传入报告的模板id
传入任务id
（HTML 模板：Jinja2 + Playwright 渲染 PDF）
"""

import base64
from io import BytesIO
from typing import List, Union
from urllib.parse import quote

from fastapi import APIRouter
from pydantic import BaseModel, Field
from fastapi.responses import StreamingResponse

from ..model.template_doc import TemplateDoc
from utils.template_utils import decode_template_html
from utils.fille_template_utils import FillDataUtils
from utils.classic_html_builder import ClassicHtmlBuilder
from exceptions.error import ErrorCode
from exceptions.command_exception import APIException
from utils.log_decorator import log_response

router = APIRouter()

class InputSchema(BaseModel):
    raw_data_report_id: int = Field(None, description='报告模板id')
    test_data_report_id: int = Field(None, description='原始模板id')
    task_id: str = Field(..., description='任务id')
    sample_id: str = Field(None, description='样品id')
    analysis_id: str = Field(None, description='分析id')
    all_display: int = Field(0, description='Abs和T%是否显示')
    image_base64: str = Field(None, description='图片base64')
    export_report: bool = Field(False, description='是否导出报告，默认False')
    show_type: str = Field('', description='波峰, 波谷, 标记点')
    is_one_sample: bool = Field(False, description='是否单样品')

class OutSchema(BaseModel):
    pass


async def _render_template_html(template_id: int, task_id: str, sample_id: str, analysis_id: str,
                                image_base64: str, all_display: int, show_type: str, is_one_sample: bool = False):
    """取模板 HTML，构建 contexts 并渲染为 HTML 字符串。返回 (name, rendered_html, contexts)。"""
    template = await TemplateDoc.get_or_none(id=template_id)
    if not template:
        raise APIException(ErrorCode.TEMPLATE_NOT_FOUND)
    html_template_str = decode_template_html(template)
    if not html_template_str.strip():
        raise APIException(ErrorCode.TEMPLATE_NOT_FOUND, f"模板 {template.name} 内容为空或非 HTML")

    fill_data_utils = FillDataUtils(template.name, template=template)
    fill_data_utils.single_sample = is_one_sample
    contexts = await fill_data_utils.build_html_contexts(
        task_id=task_id, analysis_id=analysis_id, image_base64=image_base64, all_display=all_display,
        show_type=show_type, is_one_sample=is_one_sample
    )
    rendered = ClassicHtmlBuilder(template_html=html_template_str).render_html(contexts)
    return template.name, rendered, contexts


@router.post('/export_original_report_docx')
@log_response
async def export_docx(data: InputSchema):
    raw_data_report_id = data.raw_data_report_id   # 原始记录（报告模板）
    test_data_report_id = data.test_data_report_id # 测量数据（原始数据模板）
    analysis_id = data.analysis_id
    image_base64 = data.image_base64
    all_display = data.all_display
    show_type = data.show_type
    is_one_sample = data.is_one_sample
    if not raw_data_report_id and not test_data_report_id:
        raise APIException(ErrorCode.AT_LEAST_ONE_TEMPLATE_ID)
    task_id = data.task_id
    sample_id = data.sample_id

    html_parts = []
    first_contexts = {}
    report_template_name = ''

    if raw_data_report_id:
        report_template_name, rendered, first_contexts = await _render_template_html(
            raw_data_report_id, task_id, sample_id, analysis_id, image_base64, all_display, show_type=show_type, is_one_sample=is_one_sample
        )
        html_parts.append(rendered)

    if test_data_report_id:
        original_template_name, rendered, contexts = await _render_template_html(
            test_data_report_id, task_id, sample_id, analysis_id, image_base64, all_display, show_type=show_type, is_one_sample=is_one_sample
        )
        if not first_contexts:
            first_contexts = contexts
        if not report_template_name:
            report_template_name = original_template_name
        html_parts.append(rendered)

    # 拼接多个 HTML（分页符分隔）
    combined_html = '<div style="page-break-after:always;"></div>'.join(html_parts)

    # 页眉页脚/页码/边距配置取第一个模板的 contexts
    builder = ClassicHtmlBuilder(template_html=combined_html)
    pdf_bytes = builder.build_pdf_from_rendered(
        combined_html,
        header_info=first_contexts.get('__header__'),
        footer_info=first_contexts.get('__footer__'),
        page_num_info=first_contexts.get('__page_num__'),
        margin_info=first_contexts.get('__margin__'),
        orientation_info=first_contexts.get('__orientation__'),
        line_height_info=first_contexts.get('__line_height__'),
    )

    filename = f"{report_template_name}_filled.pdf"
    safe_name = quote(filename)
    return StreamingResponse(
        BytesIO(pdf_bytes),
        media_type="application/pdf",
        headers={
            "Content-Disposition": f"attachment; filename*=UTF-8''{safe_name}",
            "Content-Length": str(len(pdf_bytes)),
        },
    )