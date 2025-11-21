import json
from datetime import datetime
from cryptography.fernet import Fernet

# 生成密钥（第一次运行用）
# key = Fernet.generate_key()
# print(key)

SECRET_KEY = b'uj97h_vp5sfr73mbx76wv8T_esw0MOxrLRrOpZ2qhMk='   # 固定保存在服务器

f = Fernet(SECRET_KEY)



def encrypt_json(data: dict) -> bytes:
    raw = json.dumps(data, default=json_converter).encode("utf-8")
    encrypted = f.encrypt(raw)
    return encrypted # 返回 Bytes

def decrypt_json(base64_cipher_text: str) -> dict:
    raw = f.decrypt(base64_cipher_text.encode("utf-8"))
    return json.loads(raw.decode("utf-8"))

def json_converter(obj):
    """自定义转换函数：将 datetime 对象转换为 ISO 8601 字符串。"""
    if isinstance(obj, datetime):
        # 将 datetime 对象转换为标准 ISO 8601 字符串
        # 例如: "2025-11-20T12:07:59.000000"
        return obj.isoformat() 
    # 对于其他无法处理的类型，抛出 TypeError
    raise TypeError(f'Object of type {obj.__class__.__name__} is not JSON serializable')