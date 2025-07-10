from fastapi import APIRouter

router = APIRouter()

from .create_template_view import router as create_template_router
from .export_doc_view import router as export_doc_router
from .get_report_template_view import router as get_report_template_router
from .get_calibration_template_view import router as get_calibration_template_router
from .get_installation_acceptance_template_view import router as get_installation_acceptance_template_router
from .get_total_template_view import router as get_total_template_router
from .get_bookmark_view import router as get_bookmark_router
from .update_template import router as update_template_router
from .get_template_content_view import router as get_template_content_router
from .get_bookmark_setting import router as get_bookmark_setting_router
from .update_bookmark import router as update_bookmark_router
from .get_template_extra_info import router as get_template_extra_info_router
from .del_template_view import router as del_template_router
from .get_template_industry import router as get_template_industry_router

router.include_router(create_template_router, prefix='', tags=['导入模板'])
router.include_router(export_doc_router, prefix='', tags=['替换书签, 导出word'])
router.include_router(get_report_template_router, prefix='', tags=['获取报告模板'])
router.include_router(get_calibration_template_router, prefix='', tags=['获取校准模板'])
router.include_router(get_installation_acceptance_template_router, prefix='', tags=['获取安装验收模板'])
router.include_router(get_total_template_router, prefix='', tags=['获取所有模板'])
router.include_router(get_bookmark_router, prefix='', tags=['根据模板获取书签'])
router.include_router(update_template_router, prefix='', tags=['更新模板'])
router.include_router(get_template_content_router, prefix='', tags=['获取模板内容'])
router.include_router(get_bookmark_setting_router, prefix='', tags=['获取书签设置, 一个列表，展示了所有的字体，字号，图片尺寸'])
router.include_router(update_bookmark_router, prefix='', tags=['更新书签'])
router.include_router(get_template_extra_info_router, prefix='', tags=['获取模板额外信息, 标题，页眉，页脚'])
router.include_router(del_template_router, prefix='', tags=['删除模板'])
router.include_router(get_template_industry_router, prefix='', tags=['获取模板行业'])