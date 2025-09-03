from tortoise import fields
from tortoise.models import Model

class BookmarkData(Model):
    id = fields.IntField(primary_key=True)
    bookmark_id = fields.IntField()
    value = fields.CharField(max_length=255, null=True, help_text='普通文字')
    structure_type = fields.SmallIntField(default=0, help_text='表格数据类型 0: 横向表头, 1: 纵向表头')
    table_structure = fields.JSONField(null=True, help_text='表结构')
    create_datetime = fields.DatetimeField(auto_now_add=True)
    update_datetime = fields.DatetimeField(auto_now=True)
    is_del = fields.SmallIntField(default=0)

    class Meta:
        table = "bookmark_data"
        indexes = [
            ("bookmark_id",)
        ]