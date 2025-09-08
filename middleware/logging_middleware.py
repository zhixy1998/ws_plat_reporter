import time
import json
import uuid
from typing import Callable, Dict, Any
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from utils.logger import logger
import traceback
from datetime import datetime

# 导入上下文变量设置函数
from utils.log_decorator import set_request_context

# 全局存储请求信息，供装饰器使用
_request_store: Dict[str, Dict[str, Any]] = {}

class LoggingMiddleware(BaseHTTPMiddleware):
    """简化的日志中间件 - 只记录请求信息和基本响应状态"""
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # 生成唯一请求ID
        request_id = str(uuid.uuid4()).replace("-", "")[:16]
        start_time = time.time()
        
        # 获取请求信息
        method = request.method
        url = request.url
        query_params = dict(request.query_params) if request.query_params else None
        headers = dict(request.headers)
        
        # 过滤敏感头信息
        safe_headers = {k: v for k, v in headers.items() 
                       if k.lower() not in ['authorization', 'token', 'cookie']}
        
        # 读取请求体 - 使用更安全的方式
        body = None
        if request.method in ["POST", "PUT", "PATCH"]:
            try:
                # 检查 Content-Type 来决定如何处理请求体
                content_type = request.headers.get("content-type", "")
                
                if "application/json" in content_type:
                    try:
                        body = await request.json()
                    except Exception:
                        body = "<invalid-json>"
                elif "multipart/form-data" in content_type:
                    body = "<multipart-form-data>"
                elif "application/x-www-form-urlencoded" in content_type:
                    try:
                        form_data = await request.form()
                        body = dict(form_data)
                    except Exception:
                        body = "<form-data-error>"
                else:
                    # 对于其他类型，只记录类型信息，不读取内容
                    body = f"<{content_type or 'unknown-content-type'}>"
                    
            except Exception as e:
                logger.warning(f"读取请求体失败: {e}")
                body = f"<error: {str(e)}>"
        
        # 创建请求日志记录
        request_info = {
            "request_id": request_id,
            "timestamp": datetime.now().isoformat(),
            "method": method,
            "url": str(url),
            "query_params": query_params,
            "headers": safe_headers,
            "request_body": body,
            "start_time": start_time
        }
        
        # 存储请求信息，供后续使用
        _request_store[request_id] = request_info
        
        # 将 request_id 添加到请求状态中，供路由使用
        request.state.request_id = request_id
        request.state.start_time = start_time
        request.state.request_info = request_info
        
        # 设置 Request 上下文，供装饰器使用
        set_request_context(request)
        
        # 记录请求开始
        logger.info(f"[请求开始] ID: {request_id} {method} {url}")
        logger.debug(f"请求详情:\n{json.dumps(request_info, ensure_ascii=False, indent=2)}")
        
        try:
            # 调用下一个中间件或路由处理器
            response = await call_next(request)
            
            # 计算执行时间
            execution_time = time.time() - start_time
            
            # 记录基本响应信息（不读取响应体）
            logger.info(f"[请求完成] ID: {request_id} Status: {response.status_code} Time: {round(execution_time * 1000, 2)}ms")
            
            return response
            
        except Exception as e:
            # 计算执行时间
            execution_time = time.time() - start_time
            
            # 记录错误信息
            error_info = {
                "request_id": request_id,
                "error_type": type(e).__name__,
                "error_message": str(e),
                "execution_time_ms": round(execution_time * 1000, 2),
                "request_info": request_info,
                "traceback": traceback.format_exc()
            }
            
            logger.error(f"[请求异常] ID: {request_id}\n{json.dumps(error_info, ensure_ascii=False, indent=2)}")
            
            # 清理存储
            _request_store.pop(request_id, None)
            
            # 重新抛出异常
            raise e
        finally:
            # 清理过期的请求信息（防止内存泄漏）
            _request_store.pop(request_id, None)

def get_request_info(request_id: str) -> Dict[str, Any]:
    """获取请求信息"""
    return _request_store.get(request_id)

def log_complete_request(request_id: str, response_data: Any, status_code: int = 200):
    """记录完整的请求-响应日志"""
    request_info = _request_store.get(request_id)
    if not request_info:
        logger.warning(f"未找到请求ID {request_id} 的信息")
        return
    
    execution_time = time.time() - request_info["start_time"]
    
    # 创建完整日志记录
    complete_log = {
        "request_id": request_id,
        "timestamp": request_info["timestamp"],
        "method": request_info["method"],
        "url": request_info["url"],
        "query_params": request_info["query_params"],
        "headers": request_info["headers"],
        "request_body": request_info["request_body"],
        "response": {
            "status_code": status_code,
            "body": response_data
        },
        "execution_time_ms": round(execution_time * 1000, 2),
        "status": "completed"
    }
    
    # 记录完整日志
    logger.info(f"📋 [完整请求日志] ID: {request_id}\n{json.dumps(complete_log, ensure_ascii=False, indent=2, cls=DateTimeEncoder)}")
    
    # 清理存储
    _request_store.pop(request_id, None)



class DateTimeEncoder(json.JSONEncoder):
    """自定义 JSON 编码器，处理 datetime 对象和文件流对象"""
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.isoformat()  # 转换为 ISO 格式字符串
        
        # 处理文件流对象
        if hasattr(obj, 'read') and hasattr(obj, 'name'):
            return f"<FileStream: {getattr(obj, 'name', 'unknown')}>"
        
        # 处理其他类似文件的对象
        if hasattr(obj, 'read'):
            return f"<FileObject: {type(obj).__name__}>"
        
        # 处理字节对象
        if isinstance(obj, bytes):
            return f"<bytes: {len(obj)} bytes>"
        
        # 处理其他不可序列化的对象
        try:
            return str(obj)
        except Exception:
            return f"<{type(obj).__name__}: non-serializable>"