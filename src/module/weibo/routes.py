from fastapi import APIRouter, HTTPException
from typing import Optional
from pydantic import BaseModel
from src import Weibo
from src.utils import get_app_logger

# 获取应用日志器
logger = get_app_logger()

# 创建路由器
router = APIRouter(
    prefix="/weibo",
    tags=["weibo"],
    responses={404: {"description": "Not found"}},
)

# 定义请求参数模型 - Tiktok
class WeiboParams(BaseModel):
    url: str
    type: Optional[str] = "png"
    format: Optional[str] = "json"

# 无前缀的POST端点
@router.post("/analyze")
async def process_weibo(params: WeiboParams):
    """
    处理微博 URL 并返回数据
    
    参数:
    - url: 微博链接
    - type: 图片类型，支持 "png" 或 "webp"
    - format: 返回格式，支持 "json" 或 "html"
    """
    logger.info(f"处理微博URL (POST): {params.url}")
    try:
        weibo = Weibo(params.url)
        
        if params.format.lower() == "html":
            # 返回 HTML 内容
            logger.info(f"返回HTML内容，长度: {len(weibo.html) if weibo.html else 0}")
            return {
                'code': 200,
                'data': weibo.html,
                'status': 'success',
                'message': '获取成功'
            }
        else:
            # 返回结构化数据
            logger.info("返回结构化数据")
            return {
                'code': 200,
                'data': weibo.to_dict(),
                'status': 'success',
                'message': '获取成功'
            }
    except Exception as e:
        logger.error(f"处理抖音URL出错: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))