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
    report_template_id: int = Field(None, description='报告模板id')
    original_template_id: int = Field(None, description='原始模板id')
    task_id: str = Field(..., description='任务id')
    sample_id: str = Field(None, description='样品id')

class OutSchema(BaseModel):
    pass

@router.post('/export_original_report_docx')
@log_response
async def export_docx(data: InputSchema):
    report_template_id = data.report_template_id
    original_template_id = data.original_template_id
    if not report_template_id and not original_template_id:
        raise APIException(ErrorCode.AT_LEAST_ONE_TEMPLATE_ID)
    task_id = data.task_id
    sample_id = data.sample_id
    if report_template_id:
        report_template_name, report_doc_steam_obj = await get_doc_name_and_doc_stream_obj(report_template_id)
        fill_data_instance_report = FillDataUtils(report_template_name, template_id=report_template_id)
        report_doc_steam_obj = await fill_data_instance_report.fill_data(report_doc_steam_obj, task_id, sample_id,report_template_id)
        doc_report = Document(report_doc_steam_obj)
        lock_table_width_on_document(doc_report)

    if original_template_id:
        original_template_name, original_doc_stream_obj = await get_doc_name_and_doc_stream_obj(original_template_id)
        fill_data_instance_original = FillDataUtils(original_template_name, template_id=original_template_id)
        original_doc_stream_obj = await fill_data_instance_original.fill_data(original_doc_stream_obj, task_id, sample_id,original_template_id)
        doc_original = Document(original_doc_stream_obj)
        lock_table_width_on_document(doc_original)

    if report_template_id and original_template_id:
        # 清理第一个文档末尾，避免空白页
        clean_document_for_merge(doc_report)
        
        # add_section_page_break(doc_report)
        
        # 清理第二个文档，避免空白页
        clean_document_for_merge(doc_original)
        
        composer = Composer(doc_report)
        composer.append(doc_original)

        doc_stream = BytesIO()
        composer.save(doc_stream)
        doc_stream.seek(0)
    
        # # 返回文件
        return StreamingResponse(doc_stream, media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document", headers={
            "Content-Disposition": "attachment; filename=filled.docx"
        })
    elif report_template_id and not original_template_id:
        report_doc_steam_obj.seek(0)
        return StreamingResponse(report_doc_steam_obj, media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document", headers={
            "Content-Disposition": "attachment; filename=filled.docx"
        })
    elif original_template_id and not report_template_id:
        original_doc_stream_obj.seek(0)
        return StreamingResponse(original_doc_stream_obj, media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document", headers={
            "Content-Disposition": "attachment; filename=filled.docx"
        })