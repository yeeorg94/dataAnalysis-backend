from fastapi import FastAPI

# 导入各个模块的路由
from .xiaohongshu import router as xiaohongshu_router
from .tiktok import router as tiktok_router
from .weibo import router as weibo_router
from .kuaishou import router as kuaishou_router
from .test import router as test_router
from .system import router as system_router
def register_routes(app: FastAPI):
    """
    注册所有路由模块到 FastAPI 应用
    
    参数:
    - app: FastAPI 应用实例
    """
    # 注册小红书路由
    app.include_router(xiaohongshu_router)
    # 注册抖音路由
    app.include_router(tiktok_router)
    # 注册快手路由
    app.include_router(kuaishou_router)
    # 注册微博路由
    app.include_router(weibo_router)
    # 注册测试路由
    app.include_router(test_router)
    # 注册系统路由
    app.include_router(system_router)
    
    # 在这里注册其他路由模块
    # app.include_router(douyin_router)
    # app.include_router(weibo_router)
    # 等等... 