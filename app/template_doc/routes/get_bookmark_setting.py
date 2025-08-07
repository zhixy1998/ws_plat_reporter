
from typing import List, Optional, Dict, Union
from fastapi import APIRouter
from ..model.template_bookmark import TemplateBookmark
from pydantic import BaseModel, Field
from constants.template_constant import WordFontType, WordFontSize, WordImageSizeType
from utils.log_decorator import log_response
router = APIRouter()


class DataSchema(BaseModel):
    word_font_type: List[Dict[str, Union[str, int]]] = Field({}, description='字体类型')
    word_font_size: List[Dict[str, Union[str, int]]] = Field({}, description='字体大小')
    word_img_size: List[Dict[str, Union[str, int]]] = Field({}, description='图片大小')

class OutSchema(BaseModel):
    code: int = Field(0, description='状态码')
    message: str = Field('获取成功', description='返回信息')
    data: DataSchema = Field(..., description='返回数据')

@router.get('/get_bookmark_setting', response_model=OutSchema)
@log_response
def get_bookmark_setting():
    data = {
        'word_font_type': [{ 'name': k, 'value': v}  for k, v in WordFontType.generate_decs_value_map().items()],  # 去除未知WordFontType.generate_decs_value_map().items(),
        'word_font_size': [{'name': k, 'value': v} for k, v in WordFontSize.generate_decs_value_map().items()],  # 去除未知WordFontSize.generate_decs_value_map().items(),
        'word_img_size': [{'name': k, 'value': v} for k, v in WordImageSizeType.generate_decs_value_map().items()],  # 去除未知WordImageSizeType.generate_decs_value_map().items(),
    }
    return {'code': 200, 'message': '获取成功', 'data': data}