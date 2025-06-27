import base64
from io import BytesIO

from fastapi import APIRouter, UploadFile, File, Form
from tortoise.transactions import in_transaction
from ..model.template_doc import TemplateDoc
from ..model.template_bookmark import TemplateBookmark
from utils.LoadAndDelete import get_word_bookmarks
from exceptions.error import ErrorCode
from exceptions.command_exception import APIException

router = APIRouter()

# class InputSchema(BaseModel):
#     name: str = Field(None, description='模板名称')

@router.post('/upload_template')
async def create_template_view(
    name: str = Form(None, description='模板名称'),
    file: UploadFile = File(..., description='模板文件')
    ):
    try:
        name = name if name else file.filename
        content = await file.read()
        content_base64 = base64.b64encode(content).decode('utf-8')
        # 存入数据库
        await create_template(name, content_base64, content)
    except Exception as e:
        raise APIException(ErrorCode.SAVE_TEMPLATE_FAILED)
    return {'code': 200, 'message': '模板保存成功'}

async def create_template(name: str, content_base64: str, content: bytes):
    async with in_transaction() as connnection:
        create_info = {
            'name': name,
            'template_content': content_base64
        }
        template =  await TemplateDoc.create(**create_info)
        book_markets = get_word_bookmarks(BytesIO(content))
        for book_mark in book_markets:
            pass
            await recursion_create_bookmark(book_mark, template.id)     

async def recursion_create_bookmark(bookmark, template_id, parent_id=None):
    if bookmark.get('name') and bookmark.get('id') and bookmark.get('type') is not None:
        create_info = {
            'name': bookmark['name'],
            'type': bookmark['type'],
            'description': bookmark['description'] if bookmark.get('description') else None,
            'sort_order': bookmark['sort_order'] if bookmark.get('sort_order') else 0,
            'parent_id': parent_id,
            'template_doc_id': template_id,
            'font': bookmark['font'] if bookmark.get('font') else None,
            'font_size': bookmark['font_size'] if bookmark.get('font_size') else None,
            'image_size': bookmark['image_size'] if bookmark.get('image_size') else None
        }
        new_bookmark = await TemplateBookmark.create(**create_info)
        for child in bookmark['children']:
            if child.get('name') and child.get('id'):
                await recursion_create_bookmark(child, template_id, new_bookmark.id)