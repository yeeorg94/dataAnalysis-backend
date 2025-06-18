from fastapi import FastAPI
from .inpainting_controller import router as inpainting_router

def register_controllers(app: FastAPI):
    """
    统一注册所有 controller 路由
    """
    app.include_router(inpainting_router, prefix="/api/v1/inpaint") 