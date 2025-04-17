from fastapi import APIRouter, Request, Query
from src.models.tracking import TrackingEvent, SourcePlatform
from src.services.tracking_service import TrackingService
from src.utils.response import Response
from typing import Optional
from src.utils.logger import get_tracking_logger

logger = get_tracking_logger()

router = APIRouter(prefix="/tracking", tags=["tracking"])
tracking_service = TrackingService()

@router.post("/event")
async def track_event(event: TrackingEvent, request: Request):
    """
    记录埋点事件
    
    请求示例:
    {
        "user_id": 12345,
        "source_platform": "pc",
        "event_type": "page_view",
        "event_params": {
            "page": "/home",
            "stay_time": 30
        }
    }
    """
    # 获取客户端信息
    event.user_agent = request.headers.get("user-agent")
    event.ip_address = request.client.host
    event.referrer = request.headers.get("referer")
    
    success = tracking_service.track_event(event)
    if success:
        return Response.success(None, "埋点记录成功")
    return Response.error("埋点记录失败")

@router.get("/events")
async def get_events(
    event_type: Optional[str] = Query(None, description="事件类型"),
    source_platform: Optional[SourcePlatform] = Query(None, description="来源平台"),
    user_id: Optional[int] = Query(None, description="用户ID"),
    limit: int = Query(100, ge=1, le=1000, description="返回数量限制")
):
    """
    获取埋点事件列表
    支持按事件类型、来源平台、用户ID筛选
    """
    events = tracking_service.get_events(
        event_type=event_type,
        source_platform=source_platform.value if source_platform else None,
        user_id=user_id,
        limit=limit
    )
    return Response.success(events, "获取成功") 