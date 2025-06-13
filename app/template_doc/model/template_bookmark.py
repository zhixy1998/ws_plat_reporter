
from tortoise import fields
from tortoise.models import Model

class TemplateBookmark(Model):
    id = fields.IntField(pk=True)
    parent_id = fields.IntField(null=True)
    template_doc_id = fields.IntField()
    name = fields.CharField(max_length=255)
    type = fields.IntField(max_length=10, default=0)  # 0:text 1: sheet 2:image
    description = fields.TextField(null=True)
    sort_order = fields.IntField(null=True, default=0)

    class Meta:
        table = "template_bookmark"
        indexes = [
            ("template_doc_id",),  # 单列索引
            ("parent_id",),  # 联合索引，常用
            ("name",),  # 例如你后续可能做标签名称查询
        ]