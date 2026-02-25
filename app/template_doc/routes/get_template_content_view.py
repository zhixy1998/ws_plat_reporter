import base64
import importlib
import inspect
from io import BytesIO

from tortoise import connections
from fastapi import APIRouter, UploadFile, File, Form
from pydantic import BaseModel, Field
from ..model.template_doc import TemplateDoc
from ..model.template_bookmark import TemplateBookmark
# from utils.LoadAndDelete import get_word_bookmarks
from exceptions.error import ErrorCode
from exceptions.command_exception import APIException
from utils.fille_template_utils import FillDataUtils
from utils.log_decorator import log_response
from constants.template_constant import MeasureMode
from config import config

router = APIRouter()

class DataSchema(BaseModel):
    template_content: str
    module_code: str


class OutSchema(BaseModel):
    code: int = Field(0, description='状态码')
    message: str = Field('获取成功', description='返回信息')
    data: DataSchema = Field(..., description='返回数据')


@router.get('/get_template_content', response_model=OutSchema)
@log_response
async def get_template_content(template_id: int, measure_mode: int):
    class_db_con = connections.get('classic_db')
    if measure_mode == MeasureMode.classic.value:
        template = await TemplateDoc.get_or_none(id=template_id, is_del=0).using_db(class_db_con)
    else:
        template = await TemplateDoc.get_or_none(id=template_id)
    if not template:
        raise APIException(ErrorCode.TEMPLATE_NOT_FOUND)

    # 1. 将base64解码为字节流
    content_bytes = base64.b64decode(template.template_content)
    doc_stream = BytesIO(content_bytes)
    
    # 2. 使用FillDataUtils去除docxtpl标识符
    # cleaned_stream = FillDataUtils.fill_template_jinja_blank(doc_stream=doc_stream)
    
    # 3. 读取处理后的内容并重新编码为base64
    # cleaned_stream.seek(0)
    cleaned_bytes = doc_stream.read()
    cleaned_base64 = base64.b64encode(cleaned_bytes).decode('utf-8')


    # 获取私有文件
    if measure_mode == MeasureMode.classic.value:
        module_name = config.classic_structure_module + "." + template.name  # 比如 name = "my_template"
    else:
        module_name = config.structure_module + "." + template.name  # 比如 name = "my_template"
    try:
        private_mod = importlib.import_module(module_name)
        source_code = inspect.getsource(private_mod)
    except Exception as e:
        raise APIException(error=ErrorCode.TEMPLATE_NOT_FOUND)
    

    return {'code': 200, 'message': '获取成功', 'data': {'template_content': cleaned_base64, 
            'module_code': source_code}}