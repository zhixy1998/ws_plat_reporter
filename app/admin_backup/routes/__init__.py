
from fastapi import APIRouter
from .admin_backup_view import router as admin_backup_router

router = APIRouter()


router.include_router(admin_backup_router, prefix='', tags=['导入导出数据'])