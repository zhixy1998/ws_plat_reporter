
import jwt
from fastapi import FastAPI
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
from jwt import ExpiredSignatureError, PyJWTError, InvalidTokenError

from app.db import init_db
from contextlib import asynccontextmanager
from exceptions.command_exception import APIException
from middleware.logging_middleware import LoggingMiddleware
from app.template_doc.routes import router as template_doc_router
from utils.logger import logger, format_error_log

KEY = "px_iNexus"
ALGORITHM = "HS256"

@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield

app = FastAPI(lifespan=lifespan)

origins = [
    "http://localhost:3000",  # 本地开发用
    "http://127.0.0.1:3000",
    "http://your-production-frontend.com",  # 生产环境用
    "*"  # 测试用，放开所有，生产不要随便用 *
]

app.include_router(template_doc_router, prefix='/template')


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


def verify(token: str) -> bool:
    try:
        payload = jwt.decode(token, KEY, algorithms=[ALGORITHM], issuer="auth0")
        # print("认证通过：")
        # print(f"issuer: {payload.get('iss')}")
        # print(f"username: {payload.get('userName')}")
        # print(f"过期时间： {payload.get('exp')}")
        return True
    except ExpiredSignatureError:
        # print("Token has expired")
        return False
    except InvalidTokenError:
        # print("Invalid token")
        return False

class JWTVerificationMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        if request.method == "OPTIONS":
            return JSONResponse(status_code=200, content={})
        token = request.headers.get("Token")
        if token:
            verify_result = verify(token)
            if verify_result is False:
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
)