import os
import configparser
import tempfile
from pathlib import Path
from cryptography.fernet import Fernet

class Config:
    def __init__(self, config_path: str = None):
        self.config = configparser.ConfigParser()
        # 默认从 exe 运行目录（或当前工作目录）查找 config.ini
        if config_path is None:
            config_path = Path(__file__).parent.parent / "ws_plat_reporter.ini"  # 假设 config.py 在 src 子目录，调整路径
            # 或者使用 os.getcwd() 获取当前目录：config_path = Path(os.getcwd()) / "config.ini"
        if not config_path.exists():
            raise FileNotFoundError(f"Config file not found: {config_path}")
        self.config.read(config_path, encoding='utf-8')
    
    # 步骤1：生成和当前电脑相同的密钥
    def get_cipher(self):
        # uid = wmi.WMI().Win32_ComputerSystemProduct()[0].UUID
        # key = base64.urlsafe_b64encode(uid.encode().ljust(32)[:32])
        # print(key)
        key = b'Qjc0QUIzODAtNkJFRS0xMUYwLTg5OTktREVDMDYzQUE='
        return Fernet(key)


    # 步骤2：创建解密函数
    def decrypt_value(self, raw: str) -> str:
        if not raw or not str(raw).startswith("ENC:"):
            return raw  # 不是加密值，直接返回
        try:
            cipher = self.get_cipher()
            return cipher.decrypt(raw[4:].encode()).decode()  # 跳过 "ENC:" 前缀解密
        except:
            return "ERROR_KEY"  # 解密失败

    @property
    def database_url(self):
        return self.decrypt_value(self.config.get('database', 'DB_URL'))
    
    @property
    def classic_database_url(self):
        return self.decrypt_value(self.config.get('database', 'CLASSIC_DB_URL'))
    
    @property
    def classic_template_common_var_url(self):
        return self.config.get('java_url', 'CLASSIC_TEMPLATE_COMMON_VAR_URL')
    
    @property
    def classic_template_table_head_data_url(self):
        return self.config.get('java_url', 'CLASSIC_TEMPLATE_TABLE_HEAD_DATA_URL')
    
    @property
    def port(self):
        return int(self.config.get('env', 'report_port'))
    
    @property
    def log_level(self):
        return self.config.get('env', 'report_log_level')
    
    @property
    def libre_office_path(self):
        return self.config.get('env', 'libre_office_path')
    
    @property
    def report_worker(self):
        return int(self.config.get('env', 'report_worker'))
    
    @property
    def deploy_python_path(self):
        try:
            reporter_path = Path(self.config.get('python', 'reporter_path'))
            deploy_python_path = reporter_path.parent
            return str(deploy_python_path)
        except Exception:
            return None
    
    @property
    def guide_template_table_url(self):
        return self.config.get('guide', 'TEMPLATE_COMMON_TABLE_URL')
    
    @property
    def guide_template_common_var_url(self):
        return self.config.get('guide', 'TEMPLATE_COMMON_VAR_URL')
    
    @property
    def guide_template_table_head_data_url(self):
        return self.config.get('guide', 'TEMPLATE_TABLE_HEAD_DATA_URL')


    # 添加更多 getter 方法...

# 在 main.py 或其他入口文件中使用
config = Config()