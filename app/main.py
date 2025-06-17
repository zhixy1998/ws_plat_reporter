from fastapi import FastAPI
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
from app.db import init_db
from exceptions.command_exception import APIException
from fastapi.middleware.cors import CORSMiddleware
from app.template_doc.routes import router as template_doc_router

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
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,        # 允许的源
    allow_credentials=True,       # 允许携带 cookie
    allow_methods=["*"],          # 允许所有方法
    allow_headers=["*"],          # 允许所有请求头
)

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