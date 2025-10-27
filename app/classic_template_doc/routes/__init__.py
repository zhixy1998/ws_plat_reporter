from fastapi import APIRouter

router = APIRouter()

from .classic_create_template_view import router as create_template_router
from .classic_export_original_data_doc_view import router as classic_export_original_data_doc_router
from .classic_templates import router as classic_templates_router
from .preview_template import router as preview_template_router

router.include_router(create_template_router, prefix='', tags=['导入经典模式模板'])
router.include_router(classic_export_original_data_doc_router, prefix='', tags=['导出单独原始数据'])
router.include_router(classic_templates_router, prefix='', tags=['经典模式模板所有模版'])
router.include_router(preview_template_router, prefix='', tags=['预览经典模式模板'])