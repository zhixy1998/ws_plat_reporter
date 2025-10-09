from fastapi import APIRouter

router = APIRouter()

from .classic_create_template_view import router as create_template_router
from .classic_export_original_data_doc_view import router as classic_export_original_data_doc_router

router.include_router(create_template_router, prefix='', tags=['导入经典模式模板'])
router.include_router(classic_export_original_data_doc_router, prefix='', tags=['导出单独原始数据'])