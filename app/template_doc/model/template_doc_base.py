
from tortoise import fields
from tortoise.models import Model

class TemplateDocBase(Model):
    id = fields.IntField(primary_key=True)
    name = fields.CharField(max_length=255)
    type = fields.SmallIntField(default=0, help_text="模板类型 常量 TemplateType")
    industry_type = fields.CharField(max_length=255, null=True, help_text="行业类型")
    experiment_type = fields.SmallIntField(default=0, help_text="实验类型 常量 ExperimentType")
    origin_type = fields.SmallIntField(default=0, help_text="模板来源类型 常量 TemplateOriginType")
    create_datetime = fields.DatetimeField(auto_now_add=True)
    update_datetime = fields.DatetimeField(auto_now=True)
    template_content = fields.BinaryField()  # Base64 存储doc内容（二进制，避免字符集转码）
    is_del = fields.SmallIntField(default=0)


    class Meta:
        table = "template_doc_base"