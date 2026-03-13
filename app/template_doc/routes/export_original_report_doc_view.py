"""
传入原始数据的模版id
传入报告的模版id
传入任务id
"""

import base64
from io import BytesIO
from typing import List, Union
from urllib.parse import quote

from docx import Document
from fastapi import APIRouter
from numpy import test
from pydantic import BaseModel, Field
from docxcompose.composer import Composer
from fastapi.responses import StreamingResponse

from ..model.template_doc import TemplateDoc
from utils.template_utils import get_doc_name_and_doc_stream_obj, convert_docx_to_pdf_bytes
from utils.fille_template_utils import FillDataUtils
from exceptions.error import ErrorCode
from exceptions.command_exception import APIException
from utils.log_decorator import log_response
from constants.template_constant import TemplatePageNumType

router = APIRouter()

class InputSchema(BaseModel):
    raw_data_report_id: int = Field(None, description='报告模板id')
    test_data_report_id: int = Field(None, description='原始模板id')
    task_id: str = Field(..., description='任务id')
    sample_id: str = Field(None, description='样品id')
    analysis_id: str = Field(None, description='分析id')
    image_base64: str = Field(None, description='图片base64')
    export_report: bool = Field(False, description='是否导出报告，默认False')

class OutSchema(BaseModel):
    pass

@router.post('/export_original_report_docx')
@log_response
async def export_docx(data: InputSchema):
    raw_data_report_id = data.raw_data_report_id # 原始记录
    test_data_report_id = data.test_data_report_id # 测量数据
    analysis_id = data.analysis_id
    image_base64 = data.image_base64
    if not raw_data_report_id and not test_data_report_id:
        raise APIException(ErrorCode.AT_LEAST_ONE_TEMPLATE_ID)
    # task_id = "61aa663028192bcc8d73b54562af000d"
    task_id = data.task_id
    sample_id = data.sample_id
    if raw_data_report_id: # 原始记录
        report_template_name, report_doc_steam_obj = await get_doc_name_and_doc_stream_obj(raw_data_report_id)
        template = await TemplateDoc.get_or_none(id=raw_data_report_id)
        fill_data_instance_report = FillDataUtils(report_template_name, template=template)
        report_doc_steam_obj = await fill_data_instance_report.fill_data(report_doc_steam_obj, task_id, sample_id,  raw_data_report_id, image_base64=image_base64, analysis_id=analysis_id)
        # 合并前先移除页码，最后统一插入
        if raw_data_report_id and test_data_report_id:
            report_doc_steam_obj = fill_data_instance_report.remove_header_page_number(report_doc_steam_obj)
        doc_report = Document(report_doc_steam_obj)
        # lock_table_width_on_document(doc_report)

    if test_data_report_id: # 测量数据
        original_template_name, original_doc_stream_obj = await get_doc_name_and_doc_stream_obj(test_data_report_id)
        template = await TemplateDoc.get_or_none(id=test_data_report_id)
        fill_data_instance_original = FillDataUtils(original_template_name, template=template)
        original_doc_stream_obj = await fill_data_instance_original.fill_data(original_doc_stream_obj, task_id, sample_id, test_data_report_id, image_base64=image_base64, analysis_id=analysis_id)
        if raw_data_report_id and test_data_report_id:
            original_doc_stream_obj = fill_data_instance_original.remove_header_page_number(original_doc_stream_obj)
        doc_original = Document(original_doc_stream_obj)
        # lock_table_width_on_document(doc_original)

    if raw_data_report_id and test_data_report_id:
        # 合并前：记住第二个文档每一节的页面方向和尺寸
        orig_section_props = []
        for sec in doc_original.sections:
            orig_section_props.append({
                'orientation': sec.orientation,
                'width': sec.page_width,
                'height': sec.page_height,
            })
        report_sec_count = len(doc_report.sections)

        # 在第一个文档末尾加分节符（下一页），确保第二个文档从新页开始
        from docx.enum.section import WD_SECTION
        new_section = doc_report.add_section(WD_SECTION.NEW_PAGE)
        # 让这个新节采用第二个文档第一节的页面方向和尺寸
        if orig_section_props:
            new_section.orientation = orig_section_props[0]['orientation']
            new_section.page_width = orig_section_props[0]['width']
            new_section.page_height = orig_section_props[0]['height']

        # docxcompose 合并
        composer = Composer(doc_report)
        composer.append(doc_original)

        # 合并后修复：确保分页 + 恢复第二个文档各节的页面方向
        from docx.enum.section import WD_SECTION_START
        merged_sections = list(doc_report.sections)
        for i, props in enumerate(orig_section_props):
            idx = report_sec_count + i
            if idx < len(merged_sections):
                sec = merged_sections[idx]
                # 第二个文档的第一节必须从新页开始，不能紧挨第一个文档
                if i == 0:
                    sec.start_type = WD_SECTION_START.NEW_PAGE
                # 恢复该节的页面方向和尺寸
                sec.orientation = props['orientation']
                sec.page_width = props['width']
                sec.page_height = props['height']

        doc_stream = BytesIO()
        composer.save(doc_stream)
        doc_stream.seek(0)

        # 合并完成后统一插入页码（页码连续），以原始记录的配置为准
        page_num_type = fill_data_instance_report.get_page_num_alignment()
        if page_num_type != TemplatePageNumType.no_page.value:
            doc_stream = fill_data_instance_report.insert_header_page_number(doc_stream, alignment=page_num_type)

        # 删除空白页后转换为 PDF
        doc_stream = FillDataUtils.remove_blank_pages(doc_stream)
        pdf_bytes = convert_docx_to_pdf_bytes(doc_stream)
        if not pdf_bytes:
            raise APIException(ErrorCode.CONVERT_PDF_FAILED)
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
    elif raw_data_report_id and not test_data_report_id:
        # 单文档根据私有配置插入页码
        page_num_type = fill_data_instance_report.get_page_num_alignment()
        if page_num_type != TemplatePageNumType.no_page.value:
            report_doc_steam_obj = fill_data_instance_report.insert_header_page_number(report_doc_steam_obj, alignment=page_num_type)
        # 删除空白页后转换为 PDF
        report_doc_steam_obj = FillDataUtils.remove_blank_pages(report_doc_steam_obj)
        pdf_bytes = convert_docx_to_pdf_bytes(report_doc_steam_obj)
        if not pdf_bytes:
            raise APIException(ErrorCode.CONVERT_PDF_FAILED)
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
    elif test_data_report_id and not raw_data_report_id:
        # 单文档根据私有配置插入页码
        page_num_type = fill_data_instance_original.get_page_num_alignment()
        if page_num_type != TemplatePageNumType.no_page.value:
            original_doc_stream_obj = fill_data_instance_original.insert_header_page_number(original_doc_stream_obj, alignment=page_num_type)
        # 删除空白页后转换为 PDF
        pdf_bytes = convert_docx_to_pdf_bytes(original_doc_stream_obj)
        if not pdf_bytes:
            raise APIException(ErrorCode.CONVERT_PDF_FAILED)
        filename = f"{original_template_name}_filled.pdf"
        safe_name = quote(filename)
        return StreamingResponse(
            BytesIO(pdf_bytes),
            media_type="application/pdf",
            headers={
                "Content-Disposition": f"attachment; filename*=UTF-8''{safe_name}",
                "Content-Length": str(len(pdf_bytes)),
            },
        )