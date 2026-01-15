# exceptions/error_codes.py
from enum import Enum

class Error:
    def __init__(self, code: int, zh: str, en: str = None) -> None:
        self._code = code
        self._zh = zh
        self._en = en

    @property
    def code(self):
        return self._code

    @property
    def zh(self):
        return self._zh

    @property
    def en(self):
        return self._en or self._zh  # 如果英文没填，用中文代替

class ErrorCode(Enum):
    OPERATION_FAILED = Error(1001, zh="操作失败, 系统内部错误")
    INVALID_ARGUMENT = Error(1002, zh="无效的参数")
    TEMPLATE_NOT_FOUND = Error(1003, zh="模板不存在")
    SAVE_TEMPLATE_FAILED = Error(1004, zh="保存模板失败")
    REPORT_TEMPLATE_TYPE_ERROR = Error(1005, zh='报表模板类型错误 只允许传入报表模版类型')
    INVALID_DOCX_FORMAT = Error(1006, zh='模板文件无效或不是docx格式')
    TEMPLATE_NAME_EXIST = Error(1007, zh='模版名称重复，请更换名称')
    INVALID_TEMPLATE_FIELD = Error(1008, zh='word模版中，jinja语法错误')
    AT_LEAST_ONE_TEMPLATE_ID =  Error(1009, zh='至少传入一个模版id')
    TEMPLATE_SETTING_NOT_EXIST = Error(10010, zh='模版设置不存在文件不存在')
    PRIVATE_MOD_IMPORT_ERROR = Error(10011, zh='模版私有配置导入失败')
    TABLE_DATA_HANDLER_NOT_FOUND = Error(10012, zh='模版私有配置中没有TableDataHandler')
    TEMPLATE_PRIVATE_CONFIG_NOT_FOUND = Error(10013, zh='模版私有配置不存在')
    TABLE_DATA_CUSTOM_BOOKMARK_NOT_FOUND= Error(10014, zh='模版私有配置中没有custom_bookmark')
    TEMPLATE_FILE_NOT_FOUND = Error(10015, zh='模板文件不存在')
    TEMPLATE_FILE_ALREADY_EXISTS = Error(10016, zh='新模板文件名已存在')
    TEMPLATE_UPDATE_FAILED = Error(10017, zh='模板更新失败')
    INVALID_FILE_FORMAT = Error(10018, zh='无效的文件格式')
    DOCX_CONVERSION_FAILED = Error(10019, zh='DOCX文件转换失败')
    IMPORT_ERROR = Error(10020, zh='数据库操作失败')
    TEMPLATE_NAME_EMPTY = Error(10021, zh='模板名称不能为空')
    TEMPLATE_PRIVATE_CODE_INVALID = Error(10022, zh='模板私有代码无效')