"""
传入原始数据的模版id
传入报告的模版id
传入任务id
"""

import base64
from io import BytesIO
from typing import List, Union

from docx import Document
from fastapi import APIRouter
from pydantic import BaseModel, Field
from docxcompose.composer import Composer
from fastapi.responses import StreamingResponse

from ..model.template_doc import TemplateDoc
from utils.EditDocxXML import fill_word_bookmark
from constants.template_constant import TemplateBookMarkType
from utils.template_utils import get_doc_name_and_doc_stream_obj, add_section_page_break, clean_document_for_merge
from utils.fille_template_utils import FillDataUtils
from exceptions.error import ErrorCode
from exceptions.command_exception import APIException
from utils.LoadAndDelete import lock_table_width_on_document
from utils.log_decorator import log_response

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
        fill_data_instance_report = FillDataUtils(report_template_name, template_id=raw_data_report_id)
        report_doc_steam_obj = await fill_data_instance_report.fill_data(report_doc_steam_obj, task_id, sample_id,  raw_data_report_id, image_base64=image_base64, analysis_id=analysis_id)
        doc_report = Document(report_doc_steam_obj)
        # lock_table_width_on_document(doc_report)

    if test_data_report_id: # 测量数据
        original_template_name, original_doc_stream_obj = await get_doc_name_and_doc_stream_obj(test_data_report_id)
        fill_data_instance_original = FillDataUtils(original_template_name, template_id=test_data_report_id)
        original_doc_stream_obj = await fill_data_instance_original.fill_data(original_doc_stream_obj, task_id, sample_id, test_data_report_id, image_base64=image_base64, analysis_id=analysis_id)
        doc_original = Document(original_doc_stream_obj)
        # lock_table_width_on_document(doc_original)

    if raw_data_report_id and test_data_report_id:
        # 在第一个文档末尾添加分节符，确保第二个文档从新页开始
        # 并且保持第一个文档的页面方向不受影响
        from docx.enum.section import WD_SECTION
        
        # 获取第一个文档最后一个section的页面方向设置
        last_section = doc_report.sections[-1]
        original_orientation = last_section.orientation
        original_page_width = last_section.page_width
        original_page_height = last_section.page_height
        
        # 添加新的section（分节符 - 下一页）
        new_section = doc_report.add_section(WD_SECTION.NEW_PAGE)
        
        # 保持原来section的页面方向和尺寸
        new_section.orientation = original_orientation
        new_section.page_width = original_page_width
        new_section.page_height = original_page_height
        
        composer = Composer(doc_report)
        composer.append(doc_original)

        doc_stream = BytesIO()
        composer.save(doc_stream)
        doc_stream.seek(0)

        return StreamingResponse(doc_stream, media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document", headers={
            "Content-Disposition": "attachment; filename=filled.docx"
        })
    elif raw_data_report_id and not test_data_report_id:
        report_doc_steam_obj.seek(0)
        return StreamingResponse(report_doc_steam_obj, media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document", headers={
            "Content-Disposition": "attachment; filename=filled.docx"
        })
    elif test_data_report_id and not raw_data_report_id:
        original_doc_stream_obj.seek(0)
        return StreamingResponse(original_doc_stream_obj, media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document", headers={
            "Content-Disposition": "attachment; filename=filled.docx"
        })