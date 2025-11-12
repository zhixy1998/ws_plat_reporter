from .base_dal import BaseDal
from tortoise import Tortoise
from app.template_doc.model.template_bookmark import TemplateBookmark

class TemplateBookmarkDal(BaseDal):
    
    def __init__(self):
        super().__init__(model=TemplateBookmark)

# 延迟初始化，在Tortoise完成初始化后再创建实例
template_bookmark_dal = TemplateBookmarkDal()