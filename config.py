import os
import configparser
from pathlib import Path

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

    @property
    def database_url(self):
        return self.config.get('database', 'DB_URL')
    
    @property
    def classic_database_url(self):
        return self.config.get('database', 'CLASSIC_DB_URL')
    
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

    # 添加更多 getter 方法...

# 在 main.py 或其他入口文件中使用
config = Config()