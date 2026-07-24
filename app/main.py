
import jwt
from fastapi import FastAPI
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
from jwt import ExpiredSignatureError, PyJWTError, InvalidTokenError
from typing import Optional

from app.db import init_db
from contextlib import asynccontextmanager
from exceptions.command_exception import APIException
from middleware.logging_middleware import LoggingMiddleware
from app.template_doc.routes import router as template_doc_router
from app.admin_backup.routes import router as admin_backup_router
from app.classic_template_doc.routes import router as classic_template_doc_router
from utils.logger import logger, format_error_log

KEY = "px_iNexus"
ALGORITHM = "HS256"

@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    print("应用启动成功！")
    print("UV-iNexus-1.0.1.260529-INS-REL_test")
    yield

app = FastAPI(lifespan=lifespan)

origins = [
    "*"  # 测试用，放开所有，生产不要随便用 *
]

app.include_router(template_doc_router, prefix='/template')
app.include_router(classic_template_doc_router, prefix='/classic_template')
app.include_router(admin_backup_router, prefix='/admin_backup')


@app.exception_handler(APIException)
async def api_exception_handler(request: Request, exc: APIException):
    return JSONResponse(
        status_code=200,  # 固定返回 200
        content={
            "code": exc.code,
            "message": exc.message
        }
    )





class TokenAuthError(HTTPException):
    def __init__(self, status_code: int, detail: str):
        super().__init__(status_code=status_code, detail=detail)

@app.exception_handler(TokenAuthError)
async def token_auth_exception_handler(request: Request, exc: TokenAuthError):
    return JSONResponse(
        status_code=200,
        content={
            'code': exc.status_code,
            'message': exc.detail,
            'success': False
        }
    )


def verify(token: str) -> Optional[dict]:
    try:
        payload = jwt.decode(token, KEY, algorithms=[ALGORITHM], issuer="auth0")
        return payload
    except ExpiredSignatureError:
        return None
    except InvalidTokenError:
        return None

class JWTVerificationMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        if request.method == "OPTIONS":
            return JSONResponse(status_code=200, content={})
        token = request.headers.get("Token")
        if token:
            payload = verify(token)
            if not payload:
                # print(request.url.path)
                return JSONResponse(
                    status_code=200,
                    content={
                        "code": 401,
                        "message": "认证失败",
                        # "path": request.url.path,  # 可选，返回当前请求路径
                        "success": False
                    }
                )
            request.state.jwt_payload = payload
            request.state.user_name = payload.get("userName")

        response = await call_next(request)
        return response

app.add_middleware(LoggingMiddleware)
app.add_middleware(JWTVerificationMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,        # 允许的源
    allow_credentials=True,       # 允许携带 cookie
    allow_methods=["*"],          # 允许所有方法
    allow_headers=["*"],          # 允许所有请求头
    expose_headers=["Content-Disposition"] 
)