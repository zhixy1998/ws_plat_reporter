
from tortoise import fields
from tortoise.models import Model

class TemplateExtraInfo(Model):
    id = fields.IntField(primary_key=True)
    template_doc_id = fields.IntField()
    bookmark_data_id = fields.IntField()
    has_tr = fields.SmallIntField(default=0, help_text='是否包含docx的{%tr %}语法 也就是表格横向循环渲染')
    create_datetime = fields.DatetimeField(auto_now_add=True)
    update_datetime = fields.DatetimeField(auto_now=True)


    class Meta:
        table = "template_extra_info"