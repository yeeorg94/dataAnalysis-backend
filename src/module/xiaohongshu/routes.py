from fastapi import APIRouter, HTTPException
from typing import Optional
from pydantic import BaseModel
from src import Xiaohongshu
from src.utils import get_app_logger

# 获取应用日志器
logger = get_app_logger()

# 创建路由器
router = APIRouter(
    prefix="/xiaohongshu",
    tags=["xiaohongshu"],
    responses={404: {"description": "Not found"}},
)

# 定义请求参数模型 - Xiaohongshu
class XiaohongshuParams(BaseModel):
    url: str
    type: Optional[str] = "png"
    format: Optional[str] = "json"

# 无前缀的POST端点
@router.post("/analyze")
async def process_xiaohongshu(params: XiaohongshuParams):
    """
    处理小红书 URL 并返回数据
    
    参数:
    - url: 小红书链接
    - type: 图片类型，支持 "png" 或 "webp"
    - format: 返回格式，支持 "json" 或 "html"
    """
    logger.info(f"处理小红书URL (POST): {params.url}")
    try:
        xiaohongshu = Xiaohongshu(params.url, params.type)
        
        if params.format.lower() == "html":
            # 返回 HTML 内容
            logger.info(f"返回HTML内容，长度: {len(xiaohongshu.html) if xiaohongshu.html else 0}")
            return {
                'code': 200,
                'data': xiaohongshu.html,
                'status': 'success',
                'message': '获取成功'
            }
        else:
            # 返回结构化数据
            logger.info("返回结构化数据")
            return {
                'code': 200,
                'data': xiaohongshu.to_dict(),
                'status': 'success',
                'message': '获取成功'
            }
    except Exception as e:
        logger.error(f"处理小红书URL出错: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))