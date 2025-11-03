import os
import configparser
from pathlib import Path
import sys
class Config:
    def __init__(self, config_path: str = None):
        self.config = configparser.ConfigParser()
        
        if config_path is None:
            if getattr(sys, 'frozen', False):
                # 打包后：.exe 所在目录的上一层文件夹
                exe_dir = Path(sys.executable).parent  # .exe 所在目录
                config_path = exe_dir.parent / "deploy_config.ini"  # 上一层目录的配置文件
            else:
                # 本地运行：保持原有逻辑（根据实际需求调整，这里示例仍为项目同级）
                # 若本地也需要读取上一层，可改为 Path(__file__).parent.parent.parent
                exe_dir = Path(__file__).parent.parent  
                config_path = exe_dir / "deploy_config.ini"
        
        if not Path(config_path).exists():
            raise FileNotFoundError(f"Config file not found: {config_path}")
        self.config.read(config_path, encoding='utf-8')

    @property
    def database_url(self):
        return self.config.get('database', 'db_url')
    
    @property
    def classic_database_url(self):
        return self.config.get('database', 'classic_db_url')
    
    @property
    def classic_template_common_var_url(self):
        return self.config.get('java_url', 'classic_template_common_var_url')
    
    @property
    def classic_template_table_head_data_url(self):
        return self.config.get('java_url', 'classic_template_table_head_data_url')
    
    @property
    def port(self):
        return int(self.config.get('env', 'report_port'))
    
    @property
    def log_level(self):
        return self.config.get('env', 'report_log_level')

    # 添加更多 getter 方法...

# 在 main.py 或其他入口文件中使用
config = Config()