from tortoise import fields
from tortoise.models import Model
from .template_doc_base import TemplateDocBase

class TemplateDoc(TemplateDocBase):
    id = fields.IntField(primary_key=True)
    name = fields.CharField(max_length=255)
    type = fields.SmallIntField(default=0, help_text="模板类型 常量 TemplateType")
    industry_type = fields.CharField(max_length=255, null=True, help_text="行业类型")
    experiment_type = fields.SmallIntField(default=0, help_text="实验类型 常量 ExperimentType")
    create_datetime = fields.DatetimeField(auto_now_add=True)
    update_datetime = fields.DatetimeField(auto_now=True)
    template_content = fields.TextField()  # Base64 存储doc内容
    thumbnail_base64 = fields.TextField(null=True, help_text="缩略图 base64")
    base_template_id = fields.IntField(null=True, help_text='基础模版的id')
    is_del = fields.SmallIntField(default=0)
    order = fields.IntField(null=True,help_text='默认顺序')

    class Meta:
        table = "template_doc"