import os
import sys
from loguru import logger
from typing import Dict, Any
import json
from datetime import datetime
from config import config

python_path = config.deploy_python_path
if python_path:
    # 使用自定义路径的logs目录
    logs_dir = os.path.join(python_path, "logs")
else:
    # 创建logs目录
    logs_dir = "logs"
if not os.path.exists(logs_dir):
    os.makedirs(logs_dir)

# 移除默认的控制台处理器
logger.remove()

# 添加控制台输出 - 彩色格式，便于开发调试 (已禁用)
# logger.add(
#     sys.stdout,
#     format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
#     level="INFO",
#     colorize=True
# )

# 添加普通日志文件 - 记录所有请求和响应
logger.add(
    f"{logs_dir}/app.log",
    format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
    level="INFO",
    rotation="10 MB",  # 文件大小轮转
    retention="30 days",  # 保留30天
    compression="zip",  # 压缩旧日志
    encoding="utf-8"
)

# 添加错误日志文件 - 单独记录异常
logger.add(
    f"{logs_dir}/error.log",
    format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
    level="ERROR",
    rotation="10 MB",
    retention="30 days",
    compression="zip",
    encoding="utf-8"
)

def format_request_log(method: str, url: str, params: Dict[str, Any] = None, 
                      body: Any = None, headers: Dict[str, str] = None) -> str:
    """格式化请求日志"""
    log_data = {
        "type": "REQUEST",
        "method": method,
        "url": str(url),
        "timestamp": datetime.now().isoformat()
    }
    
    if params:
        log_data["query_params"] = params
    
    if body is not None:
        # 处理不同类型的请求体
        if hasattr(body, 'decode'):
            try:
                log_data["body"] = body.decode('utf-8')
            except:
                log_data["body"] = str(body)
        else:
            log_data["body"] = body
    
    if headers:
        # 过滤敏感头信息
        safe_headers = {k: v for k, v in headers.items() 
                       if k.lower() not in ['authorization', 'token', 'cookie']}
        log_data["headers"] = safe_headers
    
    return json.dumps(log_data, ensure_ascii=False, indent=2)

def format_response_log(status_code: int, response_data: Any = None, 
                       execution_time: float = None) -> str:
    """格式化响应日志"""
    log_data = {
        "type": "RESPONSE",
        "status_code": status_code,
        "timestamp": datetime.now().isoformat()
    }
    
    if execution_time is not None:
        log_data["execution_time_ms"] = round(execution_time * 1000, 2)
    
    if response_data is not None:
        # 限制响应数据大小，避免日志过大
        response_str = str(response_data)
        if len(response_str) > 1000:
            log_data["response"] = response_str[:1000] + "... (truncated)"
        else:
            log_data["response"] = response_data
    
    return json.dumps(log_data, ensure_ascii=False, indent=2)

def format_error_log(error: Exception, request_info: Dict[str, Any] = None) -> str:
    """格式化错误日志"""
    log_data = {
        "type": "ERROR",
        "error_type": type(error).__name__,
        "error_message": str(error),
        "timestamp": datetime.now().isoformat()
    }
    
    if request_info:
        log_data["request_info"] = request_info
    
    return json.dumps(log_data, ensure_ascii=False, indent=2)

# 导出logger实例
__all__ = ["logger", "format_request_log", "format_response_log", "format_error_log"]