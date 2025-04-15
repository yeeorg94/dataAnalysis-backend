from fastapi import FastAPI
from .tracking import router as tracking_router

def db_register_routes(app: FastAPI):
    app.include_router(tracking_router)