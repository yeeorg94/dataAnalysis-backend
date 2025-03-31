from fastapi import FastAPI, HTTPException
import uvicorn
import os
import sys
import logging
from typing import Optional
from pydantic import BaseModel

# Add the project root directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# 导入配置和日志模块
from src.utils import get_app_logger, config, get_environment, EnvType

# 获取应用日志器
logger = get_app_logger()

# 现在导入模块
from src import RedBook

# 根据当前环境记录信息
current_env = get_environment()
logger.info(f"应用启动于 {current_env} 环境")

# Create FastAPI application
app = FastAPI(
    title=config.API_TITLE,
    description=config.API_DESCRIPTION,
    version=config.API_VERSION,
    debug=config.DEBUG
)

# 应用启动和关闭事件
@app.on_event("startup")
async def startup_event():
    """应用启动时的事件处理"""
    logger.info(f"API 服务启动 - 环境: {current_env}")

@app.on_event("shutdown")
async def shutdown_event():
    """应用关闭时的事件处理"""
    logger.info("API 服务关闭")

# 示例用法 - 注意需要捕获异常以防止错误
# try:
#     sample_text = "http://xhslink.com/a/HaDbFXetr8F8"
#     redbook_instance = RedBook(sample_text)
#     print(f"处理的URL: {redbook_instance.url}")
#     # 仅当获取到 HTML 时打印长度，避免打印大量内容
#     if hasattr(redbook_instance, 'html') and redbook_instance.html:
#         print(f"获取的HTML长度: {len(redbook_instance.html)}")
# except Exception as e:
#     print(f"初始化 RedBook 时发生错误: {str(e)}")

# Root endpoint
@app.get("/")
async def root():
    """根端点，返回 API 信息"""
    logger.info("访问根端点")
    return {
        "message": f"欢迎使用数据分析 API - {current_env} 环境",
        "status": "运行中",
        "文档": "/docs",
        "环境": current_env
    }

# Health check endpoint
@app.get("/health")
async def health_check():
    """健康检查端点"""
    logger.info("执行健康检查")
    return {"status": "健康", "环境": current_env}

# 定义请求参数模型
class RedbookParams(BaseModel):
    url: str
    type: Optional[str] = "png"
    format: Optional[str] = "json"

# API endpoint for RedBook
@app.post("/getRedBook")
async def process_redbook(params: RedbookParams):
    """
    处理小红书 URL 并返回数据
    
    参数:
    - url: 小红书链接
    - format: 返回格式，支持 "json" 或 "html"
    """
    logger.info(f"处理小红书URL (POST): {params.url}")
    try:
        redbook = RedBook(params.url, params.type)
        
        if params.format.lower() == "html":
            # 返回 HTML 内容
            logger.info(f"返回HTML内容，长度: {len(redbook.html) if redbook.html else 0}")
            return {
                'code': 200,
                'data': redbook.html,
                'status': 'success',
                'message': '获取成功'
            }
        else:
            # 返回结构化数据
            logger.info("返回结构化数据")
            return {
                'code': 200,
                'data': redbook.to_dict(),
                'status': 'success',
                'message': '获取成功'
            }
    except Exception as e:
        logger.error(f"处理小红书URL出错: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

# 也添加一个 GET 方法的端点，方便直接在浏览器中测试
@app.get("/redbook")
async def get_redbook(url: str, format: Optional[str] = "json"):
    """
    处理小红书 URL 并返回数据（GET 方法）
    
    参数:
    - url: 小红书链接
    - format: 返回格式，支持 "json" 或 "html"
    """
    logger.info(f"处理小红书URL (GET): {url}")
    try:
        redbook = RedBook(url)
        
        if format.lower() == "html":
            # 返回 HTML 内容
            logger.info(f"返回HTML内容，长度: {len(redbook.html) if redbook.html else 0}")
            return {
                'code': 200,
                'data': redbook.html,
                'status': 'success',
                'message': '获取成功'
            }
        else:
            # 返回结构化数据
            logger.info("返回结构化数据")
            return {
                'code': 200,
                'data': redbook.to_dict(),
                'status': 'success',
                'message': '获取成功'
            }
    except Exception as e:
        logger.error(f"处理小红书URL出错: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

# 配置 uvicorn 使用文件日志而不是控制台输出
def configure_uvicorn_logging():
    """配置 uvicorn 使用文件日志"""
    # 关闭 uvicorn 默认日志
    logging.getLogger("uvicorn").handlers = []
    logging.getLogger("uvicorn.access").handlers = []
    
    # 让 uvicorn 使用我们的日志器
    logging.getLogger("uvicorn").parent = logging.getLogger("app")
    logging.getLogger("uvicorn.access").parent = logging.getLogger("app")

# Run the application with uvicorn when this script is executed directly
if __name__ == "__main__":
    # 配置 uvicorn 日志
    configure_uvicorn_logging()
    
    # 开始服务
    logger.info(f"启动 uvicorn 服务 - 主机: {config.HOST}, 端口: {config.PORT}")
    
    # 使用配置中的参数
    uvicorn.run(
        "main:app",                  # Import string to your app
        host=config.HOST,            # Host to bind the server to
        port=config.PORT,            # Port to bind the server to
        reload=config.RELOAD,        # Auto-reload when code changes
        log_level=config.LOG_LEVEL.lower(),  # Log level
        workers=1,                   # Number of worker processes
        log_config=None,             # 禁用 uvicorn 默认日志配置
        access_log=False,            # 禁用 uvicorn 访问日志
        openapi_version="3.0.2"
    )
