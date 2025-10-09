# 标准库导入


# 第三方库导入
from tortoise.models import Model
from tortoise import fields

# 本地应用导入
from exceptions.error import ErrorCode
from exceptions.command_exception import APIException
from .template_doc import TemplateDoc


class CustomBookmark(Model):
    id = fields.IntField(primary_key=True)
    header = fields.TextField(description="页眉", null=True)
    footer = fields.TextField(description="页脚", null=True)
    note = fields.TextField(description="备注", null=True)
    project_name = fields.CharField(max_length=255, description="动态项目名称", null=True)
    title = fields.TextField(description="标题", null=True)
    subtitle = fields.TextField(description="副标题", null=True)
    #和template_doc 建立虚拟外键关系
    template_doc_id = fields.IntField(description="关联的模板id")

    class Meta:
        table = "bookmark_custom"


    #根据模板id获取信息
    async def get_custom_bookmark(template_id: int):
        bookmark_custom = await CustomBookmark.get_or_none(template_doc_id=template_id)
        if not bookmark_custom:
            return None
            #raise APIException(ErrorCode.TEMPLATE_PRIVATE_CONFIG_NOT_FOUND)
        return bookmark_custom
    
    # 根据参数更新数据库数据并维护外键
    async def update_custom_bookmark(template_id: int,note: str = None, project_name: str = None, 
                                   header: str = None, footer: str = None,title: str=None,
                                   subtitle :str=None) -> bool:
        try:
            # 查找是否已存在记录
            bookmark_custom = await CustomBookmark.get_or_none(template_doc_id=template_id)
            if bookmark_custom is None:
                # 如果不存在，则创建新记录并维护外键关系
                bookmark_custom = await CustomBookmark.create(
                    template_doc_id=template_id,
                    note=note,
                    project_name=project_name,
                    header=header,
                    footer=footer,
                    subtitle=subtitle,
                    title=title
                )
            else:
                # 如果存在，则更新记录
                if note is not None:
                    bookmark_custom.note = note
                if project_name is not None:
                    bookmark_custom.project_name = project_name
                if header is not None:
                    bookmark_custom.header = header
                if footer is not None:
                    bookmark_custom.footer = footer
                if title is not None:
                    bookmark_custom.title = title
                if subtitle is not None:
                    bookmark_custom.subtitle = subtitle
                await bookmark_custom.save()
            return True
        except Exception as e:
            print(f"Error in update_custom_bookmark: {str(e)}") 
            # 记录日志或处理异常
            return False