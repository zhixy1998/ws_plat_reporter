from fastapi import APIRouter

router = APIRouter()

from .create_template_view import router as create_template_router
from .export_doc_view import router as export_doc_router
from .get_template_view import router as get_template_router
from .get_bookmark_view import router as get_bookmark_router

router.include_router(create_template_router, prefix='', tags=['导入模板'])
router.include_router(export_doc_router, prefix='', tags=['替换书签, 导出word'])
router.include_router(get_template_router, prefix='', tags=['获取模板'])
router.include_router(get_bookmark_router, prefix='', tags=['根据模板获取书签'])

