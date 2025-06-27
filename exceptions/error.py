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
