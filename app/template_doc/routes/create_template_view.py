import base64
from io import BytesIO

from fastapi import APIRouter, UploadFile, File, Form
from tortoise.transactions import in_transaction
from ..model.template_doc import TemplateDoc
from ..model.template_bookmark import TemplateBookmark
from utils.LoadAndDelete import get_word_bookmarks

router = APIRouter()

# class InputSchema(BaseModel):
#     name: str = Field(None, description='模板名称')

@router.post('/upload_template')
async def create_template(
    name: str = Form(None, description='模板名称'),
    file: UploadFile = File(..., description='模板文件')
    ):
    name = name if name else file.filename
    content = await file.read()
    content_base64 = base64.b64encode(content).decode('utf-8')
    # 存入数据库
    async with in_transaction() as connnection:
        create_info = {
            'name': name,
            'template_content': content_base64
        }
        template =  await TemplateDoc.create(**create_info)
        book_markets = get_word_bookmarks(BytesIO(content))
        for book_mark in book_markets:
            await recursion_create_bookmark(book_mark, template.id)        
    return {'code': 200, 'message': '模板保存成功'}

async def recursion_create_bookmark(bookmark, template_id, parent_id=None):
    if bookmark.get('name') and bookmark.get('id') and bookmark.get('type') is not None:
        create_info = {
            'name': bookmark['name'],
            'type': bookmark['type'],
            'description': bookmark['description'] if bookmark.get('description') else None,
            'sort_order': bookmark['sort_order'] if bookmark.get('sort_order') else 0,
            'parent_id': parent_id,
            'template_doc_id': template_id
        }
        new_bookmark = await TemplateBookmark.create(**create_info)
        for child in bookmark['children']:
            if child.get('name') and child.get('id'):
                await recursion_create_bookmark(child, template_id, new_bookmark.id)