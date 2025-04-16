from fastapi import FastAPI
from .tracking import router as tracking_router
from .analyze import router as analyze_router
from .system import router as system_router

def db_register_routes(app: FastAPI):
    app.include_router(tracking_router)
    app.include_router(analyze_router)
    app.include_router(system_router)