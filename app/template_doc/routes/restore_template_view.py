
import base64
from io import BytesIO

from pydantic import BaseModel, Field
from fastapi import APIRouter, UploadFile, File, Form
from tortoise.transactions import in_transaction
from ..model.template_doc import TemplateDoc
from ..model.template_doc_base import TemplateDocBase
from ..model.template_bookmark import TemplateBookmark
from utils.LoadAndDelete import get_word_bookmarks
from exceptions.error import ErrorCode
from exceptions.command_exception import APIException
from utils.log_decorator import log_response

router = APIRouter()


class InputSchema(BaseModel):
    id: int = Field(..., description='模板id')

@router.post('/restore_template')
@log_response
async def create_template_view(
    data: InputSchema
    ):
    try:
        id = data.id

        template_doc_instance = await TemplateDoc.get_or_none(id=id)
        if template_doc_instance is None:
            raise APIException(ErrorCode.TEMPLATE_NOT_FOUND)
        base_template_id = template_doc_instance.base_template_id
        base_template_doc_instance = await TemplateDocBase.get_or_none(id=base_template_id)
        content_base64 = base_template_doc_instance.template_content

        # 先删除 之前的这个模板的标签
        TemplateBookmark.filter(template_doc_id=id).update(is_del=1)

        # 存入
        # 第一步：解码为 bytes
        word_bytes = base64.b64decode(content_base64)
        # 第二步：用 BytesIO 包装成文件对象
        word_file = BytesIO(word_bytes)
        # 第三步：传给 get_word_bookmarks
        book_marks = get_word_bookmarks(word_file)

        for book_mark in book_marks:
            await recursion_create_bookmark(book_mark, template_doc_instance.id)     


        # 存入数据库
    except Exception as e:
        raise APIException(ErrorCode.SAVE_TEMPLATE_FAILED)
    return {'code': 200, 'message': '模板保存成功'}

async def create_template(name: str, content_base64: str, content: bytes):
    async with in_transaction('default') as connection:
        create_info = {
            'name': name,
            'template_content': content_base64
        }
        # 先创建base模型，方便以后回滚
        template_base_instance = await TemplateDocBase.create(**create_info)
        # 创建模板
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
        for child in bookmark['children']:
            if child.get('name') and child.get('id'):
                await recursion_create_bookmark(child, template_id, new_bookmark.id)