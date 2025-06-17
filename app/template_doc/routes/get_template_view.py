from typing import List, Optional
from fastapi import APIRouter
from ..model.template_doc import TemplateDoc
from utils.EditDocxXML import fill_word_bookmark

router = APIRouter()


@router.get('/get_template')
async def get_template():
    templates = await TemplateDoc.all().values('name', 'id')
    return {'code': 200, 'message': '获取成功', 'data': {'templates': templates}}