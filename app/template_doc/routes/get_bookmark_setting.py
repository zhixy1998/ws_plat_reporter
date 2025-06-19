
from typing import List, Optional, Dict
from fastapi import APIRouter
from ..model.template_bookmark import TemplateBookmark
from pydantic import BaseModel, Field
from constants.template_constant import WordFontType, WordFontSize, WordImageSizeType

router = APIRouter()


class DataSchema(BaseModel):
    word_font_type: Dict[str, str] = Field({}, description='字体类型')
    word_font_size: Dict[str, str] = Field({}, description='字体大小')
    img_size: Dict[str, str] = Field({}, description='图片大小')

class OutSchema(BaseModel):
    code: int = Field(0, description='状态码')
    message: str = Field('获取成功', description='返回信息')
    data: DataSchema = Field(..., description='返回数据')

@router.get('/get_bookmark_setting', response_model=OutSchema)
def get_bookmark_setting():
    data = {
        'word_font_type': {item.name: item.value for item in WordFontType},
        'word_font_size': {item.name: item.value for item in WordFontSize},
        'word_img_size': {item.name: item.value for item in WordImageSizeType}
    }
    return {'code': 200, 'message': '获取成功', 'data': data}