

from typing import List, Optional, Dict
from fastapi import APIRouter
from ..model.template_bookmark import TemplateBookmark
from pydantic import BaseModel, Field
from constants.template_constant import TemplateBookMarkType

router = APIRouter()

class BookmarkItem(BaseModel):
    id: int = Field(..., description="书签唯一ID")
    parent_id: Optional[int] = Field(None, description="父书签ID，用于嵌套结构")
    template_doc_id: int = Field(..., description="所属模板文档ID")
    name: str = Field(..., description="书签名称")
    type: int = Field(..., description="书签类型（1: 文本，2: 图片，3: 表格）")
    description: Optional[str] = Field(None, description="书签的详细描述")
    sort_order: int = Field(..., description="显示顺序（越小越靠前）")

class OutSchema(BaseModel):
    code: int = Field(0, description='状态码')
    message: str = Field('获取成功', description='返回信息')
    bookmarks: Dict[int, List[BookmarkItem]] = Field({}, description=f'{TemplateBookMarkType.text.value}:{TemplateBookMarkType.text.name},\
                                  {TemplateBookMarkType.sheet.value}:{TemplateBookMarkType.sheet.name},\
                                  {TemplateBookMarkType.img.value}:{TemplateBookMarkType.img.name}')

@router.get('/get_bookmark', response_model=OutSchema)
async def get_bookmark(template_id: int, type: Optional[int] = None):
    if type is not None:
        bookmarks = await TemplateBookmark.filter(template_doc_id=template_id, type=type).all().values()
    else:
        bookmarks = await TemplateBookmark.filter(template_doc_id=template_id).all().values()
        # 按 type 分组
    grouped = {}
    for item in bookmarks:
        item_type = item.get('type', 'unknown')
        grouped.setdefault(item_type, []).append(item)
    return {'code': 0, 'message': '获取成功', 'bookmarks': grouped}