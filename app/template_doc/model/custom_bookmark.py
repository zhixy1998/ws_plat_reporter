# 标准库导入


# 第三方库导入
from tortoise.models import Model
from tortoise import fields

# 本地应用导入
from exceptions.error import ErrorCode
from exceptions.command_exception import APIException
from .template_doc import TemplateDoc


class CustomBookmark(Model):
    id = fields.IntField(pk=True)
    header = fields.TextField(description="页眉", null=True)
    footer = fields.TextField(description="页脚", null=True)
    note = fields.TextField(description="备注", null=True)
    project_name = fields.CharField(max_length=255, description="动态项目名称", null=True)
    # 与 template_doc 建立虚拟外键关系
    template_doc_id = fields.IntField(description="关联的模板基础ID")

    class Meta:
        table = "bookmark_custom"


    #根据模板id获取表格信息
    async def get_custom_bookmark(template_id: int):
        bookmark_custom = await CustomBookmark.get_or_none(template_doc_id=template_id)
        if not bookmark_custom:
            raise APIException(ErrorCode.TEMPLATE_NOT_FOUND)
        return bookmark_custom
    

    # 根据参数更新数据库数据并维护外键
    async def update_custom_bookmark(template_id: int, note: str = None, project_name: str = None, 
                                   header: str = None, footer: str = None) -> bool:
        """
        根据模板ID更新或创建BookmarkCustom记录，维护与TemplateDocBase的虚拟外键关系

        Args:
            template_id (int): 关联的模板基础ID（外键）
            note (str, optional): 备注信息
            project_name (str, optional): 项目名称
            header (str, optional): 页眉内容
            footer (str, optional): 页脚内容

        Returns:
            bool: 操作成功返回True，失败返回False

        Raises:
            APIException: 当模板基础记录不存在时抛出异常
        """
        try:
            # 首先验证关联的TemplateDoc是否存在
            template_doc = await TemplateDoc.get_or_none(id=template_id)
            if template_doc is None:
                raise APIException(ErrorCode.TEMPLATE_NOT_FOUND)
            
            # 查找是否已存在关联记录`template_doc_id`
            bookmark_custom = await CustomBookmark.get_or_none(template_doc_id=template_id)
            if bookmark_custom is None:
                # 如果不存在，则创建新记录并维护外键关系
                bookmark_custom = await CustomBookmark.create(
                    template_doc_id=template_id,
                    note=note,
                    project_name=project_name,
                    header=header,
                    footer=footer
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
                await bookmark_custom.save()
            return True
        except Exception as e:
            print(f"Error in update_custom_bookmark: {str(e)}") 
            # 记录日志或处理异常
            return False