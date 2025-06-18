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
    children: List["BookmarkItem"] = Field(default_factory=list, description="子书签") # 递归用字符串引用

class BookmarkDataSchema(BaseModel):
    bookmarks: Dict[int, List[BookmarkItem]] = Field({}, description=f'{TemplateBookMarkType.text.value}:{TemplateBookMarkType.text.name},\
                                  {TemplateBookMarkType.sheet.value}:{TemplateBookMarkType.sheet.name},\
                                  {TemplateBookMarkType.img.value}:{TemplateBookMarkType.img.name}')

class OutSchema(BaseModel):
    code: int = Field(0, description='状态码')
    message: str = Field('获取成功', description='返回信息')
    data: BookmarkDataSchema

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
    result = {item_type: build_tree(bookmarks_list) for item_type, bookmarks_list in grouped.items()}
    return {'code': 200, 'message': '获取成功', 'data': {'bookmarks': result}}

def build_tree(bookmarks):
    id_node_map = {item['id']: {**item, 'children': []} for item in bookmarks}

    tree = []
    for item in bookmarks:
        node = id_node_map[item['id']]
        parent_id = item['parent_id']
        if parent_id is None:
            tree.append(node)
        else:
            parent = id_node_map[parent_id]
            if parent:
                parent['children'].append(node)
            else:
                tree.append(node)
    return tree