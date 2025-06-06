from fastapi import FastAPI
from .tracking import router as tracking_router
from .analyze import router as analyze_router
from .system import router as system_router
from .idphoto import router as idphoto_router
from src.utils.db import DatabasePool
import os

def db_register_routes(app: FastAPI):
    # 使用 DatabasePool.is_configured() 来判断是否注册数据库相关的路由
    if DatabasePool.is_configured():
        app.include_router(tracking_router)
    app.include_router(analyze_router)
    app.include_router(system_router)
    app.include_router(idphoto_router)