
from fastapi import APIRouter
from .admin_backup_view import router as admin_backup_router
from .admin_guide_backup_view import router as admin_guide_backup_router

router = APIRouter()


router.include_router(admin_backup_router, prefix='', tags=['导入导出数据'])
router.include_router(admin_guide_backup_router, prefix='', tags=['向导导入导出数据'])