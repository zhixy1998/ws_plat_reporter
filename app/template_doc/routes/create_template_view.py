import base64
from io import BytesIO
from zipfile import BadZipFile

from fastapi import APIRouter, UploadFile, File, Form
from tortoise.transactions import in_transaction
from ..model.template_doc import TemplateDoc
from ..model.template_doc_base import TemplateDocBase
from ..model.template_bookmark import TemplateBookmark
from ..model.bookmark_data import BookmarkData
from utils.LoadAndDelete import get_word_bookmarks
from exceptions.error import ErrorCode
from exceptions.command_exception import APIException
from constants.template_constant import TemplateBookMarkType

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
    except BadZipFile:
        raise APIException(ErrorCode.INVALID_DOCX_FORMAT) 
    except Exception as e:
        raise APIException(ErrorCode.SAVE_TEMPLATE_FAILED)
    return {'code': 200, 'message': '模板保存成功'}

async def create_template(name: str, content_base64: str, content: bytes):
    async with in_transaction() as connection:
        create_info = {
            'name': name,
            'template_content': content_base64
        }
        # 先创建base模型，方便以后回滚
        template_base_instance = await TemplateDocBase.create(**create_info)
        # 创建模版
        create_info['base_template_id'] = template_base_instance.id
        template =  await TemplateDoc.create(**create_info)
        # 创建标签

        book_markets = get_word_bookmarks(BytesIO(content))
        for book_mark in book_markets:
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
        # 如果是表格 并且有表格结构
        if new_bookmark.type == TemplateBookMarkType.sheet.value and bookmark.get('table_structure'):
            bookmark_id= new_bookmark.id
            structure_type = bookmark.get('table_structure').get('structure_type')
            if structure_type is not None:  # 可能是0 0也是正确的
                table_structure = bookmark.get('table_structure')
                await BookmarkData.create(bookmark_id=bookmark_id, structure_type=structure_type, table_structure=table_structure)
            
                
        for child in bookmark['children']:
            if child.get('name') and child.get('id'):
                await recursion_create_bookmark(child, template_id, new_bookmark.id)