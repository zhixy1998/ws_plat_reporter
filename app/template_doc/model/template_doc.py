from tortoise import fields
from tortoise.models import Model

class TemplateDoc(Model):
    id = fields.IntField(pk=True)
    name = fields.CharField(max_length=255)
    type = fields.IntField(max_length=10, default=0, help_text="模板类型")
    create_datetime = fields.DatetimeField(auto_now_add=True)
    update_datetime = fields.DatetimeField(auto_now=True)
    template_content = fields.TextField()  # Base64 存储doc内容

    class Meta:
        table = "template_doc"