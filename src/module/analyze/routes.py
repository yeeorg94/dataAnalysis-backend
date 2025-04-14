from typing import Optional
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from src.utils import config, get_analyze_logger

# 获取应用日志器
logger = get_analyze_logger()


class AnalyzeParams(BaseModel):
    url: str
    type: Optional[str] = "png"
    format: Optional[str] = "json"


# 创建路由器
router = APIRouter(
    prefix="/analyze",
    tags=["analyze"],
    responses={404: {"description": "Not found"}},
)


# 无前缀的POST端点
@router.post("")
async def process_analyze(params: AnalyzeParams):
    try:
        url = params.url
        app_type = ""
        # 判断url是否包含小红书或抖音
        if any(keyword in url for keyword in config.APP_TYPE_KEYWORD["xiaohongshu"]):
            app_type = "xiaohongshu"
        elif any(keyword in url for keyword in config.APP_TYPE_KEYWORD["douyin"]):
            app_type = "douyin"
        elif any(keyword in url for keyword in config.APP_TYPE_KEYWORD["kuaishou"]):
            app_type = "kuaishou"
        elif any(keyword in url for keyword in config.APP_TYPE_KEYWORD["weibo"]):
            app_type = "weibo"
        else:
            from src.utils.response import Response
            raise Response.error("不支持的URL")
        
        
        # 根据app_type选择对应的模块
        if app_type == 'xiaohongshu':
            from src.app.xiaohongshu.index import Xiaohongshu
            xiaohongshu = Xiaohongshu(url, params.type)
            return xiaohongshu.to_dict()
        elif app_type == 'douyin':
            from src.app.tiktok.index import Tiktok
            tiktok = Tiktok(url, params.type)
            return tiktok.to_dict()
        elif app_type == 'kuaishou':
            from src.app.kuaishou.index import Kuaishou
            kuaishou = Kuaishou(url, params.type)
            return kuaishou.to_dict()
        elif app_type == 'weibo':
            from src.app.weibo.index import Weibo
            weibo = Weibo(url, params.type)
            return weibo.to_dict()
        else:
            from src.utils.response import Response
            raise Response.error("请联系客服！")
    
    except Exception as e:
        logger.error(f"处理聚合数据出错: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))
