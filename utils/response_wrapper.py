import json
import time
from typing import Any, Dict
from fastapi import Response
from fastapi.responses import JSONResponse
from utils.logger import logger
from datetime import datetime
import uuid

class LoggingResponse(JSONResponse):
    """自定义响应类，自动记录日志"""
    
    def __init__(self, content: Any = None, status_code: int = 200, 
                 headers: dict = None, media_type: str = "application/json",
                 request_info: Dict[str, Any] = None, start_time: float = None):
        super().__init__(content=content, status_code=status_code, 
                        headers=headers, media_type=media_type)
        
        if request_info and start_time:
            self._log_complete_request(content, status_code, request_info, start_time)
    
    def _log_complete_request(self, content: Any, status_code: int, 
                            request_info: Dict[str, Any], start_time: float):
        """记录完整的请求-响应日志"""
        execution_time = time.time() - start_time
        
        # 创建完整的日志记录
        log_record = {
            "request_id": request_info.get("request_id", str(uuid.uuid4())[:8]),
            "timestamp": datetime.now().isoformat(),
            "method": request_info.get("method"),
            "url": request_info.get("url"),
            "query_params": request_info.get("query_params"),
            "headers": request_info.get("headers"),
            "request_body": request_info.get("body"),
            "response": {
                "status_code": status_code,
                "body": content
            },
            "execution_time_ms": round(execution_time * 1000, 2),
            "status": "completed"
        }
        
        # 记录完整日志
        logger.info(f"[完整请求日志] ID: {log_record['request_id']}\n{json.dumps(log_record, ensure_ascii=False, indent=2)}")

def create_logging_response(content: Any, status_code: int = 200, 
                          request_info: Dict[str, Any] = None, 
                          start_time: float = None) -> LoggingResponse:
    """创建带日志记录的响应"""
    return LoggingResponse(
        content=content, 
        status_code=status_code,
        request_info=request_info,
        start_time=start_time
    )
