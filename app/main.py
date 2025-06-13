from fastapi import FastAPI
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
from app.db import init_db
from exceptions.command_exception import APIException

from app.template_doc.routes import router as template_doc_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield

app = FastAPI(lifespan=lifespan)

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