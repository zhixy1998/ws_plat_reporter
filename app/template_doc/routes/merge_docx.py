from fastapi import APIRouter, UploadFile, File
from pydantic import BaseModel, Field
from fastapi.responses import StreamingResponse
from io import BytesIO
from docx import Document
from docxcompose.composer import Composer

from utils.log_decorator import log_response
from utils.table_data_processor import GetHeaderAndData
from utils.template_utils import clean_document_for_merge
from exceptions.command_exception import APIException
from exceptions.error import ErrorCode

router = APIRouter()

# 保留原有入参模型（若仍需调试用），但本接口以文件上传为主
class InputSchema(BaseModel):
    task_id: str = Field(None, description='任务id')
    sample_id: str = Field(None, description='样品id')

@router.post('/merge_docx')
@log_response
async def merge_docx(file1: UploadFile = File(...), file2: UploadFile = File(...)):
    # 基础校验：只接受 .docx
    def _is_docx(f: UploadFile) -> bool:
        filename = (f.filename or '').lower()
        return filename.endswith('.docx')

    if not (_is_docx(file1) and _is_docx(file2)):
        raise APIException(ErrorCode.INVALID_DOCX_FORMAT)

    # 读取上传内容到内存
    content1 = await file1.read()
    content2 = await file2.read()

    buf1 = BytesIO(content1)
    buf2 = BytesIO(content2)

    # 加载为 Document
    doc1 = Document(buf1)
    doc2 = Document(buf2)

    # 合并前清理，避免空白页/尾部多余节
    clean_document_for_merge(doc1)
    clean_document_for_merge(doc2)

    # 使用 Composer 合并
    composer = Composer(doc1)
    composer.append(doc2)

    out_stream = BytesIO()
    composer.save(out_stream)
    out_stream.seek(0)

    return StreamingResponse(
        out_stream,
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        headers={"Content-Disposition": "attachment; filename=merged.docx"}
    )