from fastapi import FastAPI

# 导入各个模块的路由
from .xiaohongshu import router as xiaohongshu_router

def register_routes(app: FastAPI):
    """
    注册所有路由模块到 FastAPI 应用
    
    参数:
    - app: FastAPI 应用实例
    """
    # 注册小红书路由
    app.include_router(xiaohongshu_router)
    
    # 在这里注册其他路由模块
    # app.include_router(douyin_router)
    # app.include_router(weibo_router)
    # 等等... 