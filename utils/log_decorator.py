from functools import wraps
from fastapi import Request
import inspect
from contextvars import ContextVar
from typing import Optional
from starlette.requests import Request as StarletteRequest

# 创建上下文变量来存储当前请求
_request_context: ContextVar[Optional[Request]] = ContextVar('request_context', default=None)

def get_current_request() -> Optional[Request]:
    """获取当前请求的上下文"""
    return _request_context.get()

def set_request_context(request: Request):
    """设置当前请求的上下文"""
    _request_context.set(request)

def log_response(func):
    """
    装饰器：自动记录路由的响应数据
    使用方法：在路由函数上添加 @log_response
    注意：需要在中间件中设置 request 上下文，或者在路由函数中包含 Request 参数
    """
    # 函数内部导入 防止循环调用
    from middleware.logging_middleware import log_complete_request
    @wraps(func)
    async def async_wrapper(*args, **kwargs):
        # 查找 Request 对象
        request = None
        
        # 1. 先从上下文中获取
        request = get_current_request()
        
        # 2. 如果上下文中没有，从 args 中查找
        if not request:
            for arg in args:
                if isinstance(arg, (Request, StarletteRequest)):
                    request = arg
                    set_request_context(request)
                    break
        
        # 3. 如果 args 中没有，再从 kwargs 中查找
        if not request:
            for key, value in kwargs.items():
                if isinstance(value, (Request, StarletteRequest)):
                    request = value
                    set_request_context(request)
                    break
        
        if not request:
            # 如果没有找到 Request，正常执行函数
            if inspect.iscoroutinefunction(func):
                return await func(*args, **kwargs)
            else:
                return func(*args, **kwargs)
        
        # 执行原函数
        if inspect.iscoroutinefunction(func):
            result = await func(*args, **kwargs)
        else:
            result = func(*args, **kwargs)
        
        # 记录完整的请求-响应日志
        if hasattr(request.state, 'request_id'):
            request_id = request.state.request_id
            
            # 确定状态码
            status_code = 200
            if hasattr(result, 'status_code'):
                status_code = result.status_code
            
            # 获取响应数据
            response_data = result
            if hasattr(result, 'content'):
                response_data = result.content
            elif hasattr(result, 'body'):
                response_data = result.body
            
            # 记录完整日志
            log_complete_request(request_id, response_data, status_code)
        
        return result
    
    @wraps(func)
    def sync_wrapper(*args, **kwargs):
        # 查找 Request 对象
        request = None
        
        # 1. 先从上下文中获取
        request = get_current_request()
        
        # 2. 如果上下文中没有，从 args 中查找
        if not request:
            for arg in args:
                if isinstance(arg, (Request, StarletteRequest)):
                    request = arg
                    set_request_context(request)
                    break
        
        # 3. 如果 args 中没有，再从 kwargs 中查找
        if not request:
            for key, value in kwargs.items():
                if isinstance(value, (Request, StarletteRequest)):
                    request = value
                    set_request_context(request)
                    break
        
        if not request:
            return func(*args, **kwargs)
        
        # 执行原函数
        result = func(*args, **kwargs)
        
        # 记录完整的请求-响应日志
        if hasattr(request.state, 'request_id'):
            request_id = request.state.request_id
            
            # 确定状态码
            status_code = 200
            if hasattr(result, 'status_code'):
                status_code = result.status_code
            
            # 获取响应数据
            response_data = result
            if hasattr(result, 'content'):
                response_data = result.content
            elif hasattr(result, 'body'):
                response_data = result.body
            
            # 记录完整日志
            log_complete_request(request_id, response_data, status_code)
        
        return result
    
    # 根据函数类型返回对应的包装器
    if inspect.iscoroutinefunction(func):
        return async_wrapper
    else:
        return sync_wrapper


def auto_log_response(response_data, request: Request, status_code: int = 200):
    """
    手动记录响应日志的函数
    在路由中手动调用此函数来记录响应
    """
    if hasattr(request.state, 'request_id'):
        request_id = request.state.request_id
        log_complete_request(request_id, response_data, status_code)
