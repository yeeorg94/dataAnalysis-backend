from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime
from enum import Enum

class SourcePlatform(str, Enum):
    PC = 'pc'
    H5 = 'h5'
    MINI_PROGRAM = 'mini_program'
    ANDROID = 'android'
    IOS = 'ios'

class TrackingEvent(BaseModel):
    user_id: Optional[int] = None
    source_platform: SourcePlatform
    event_type: str
    ip_address: Optional[str] = None  # 由服务器自动设置
    user_agent: Optional[str] = None
    referrer: Optional[str] = None
    event_params: Dict[str, Any]
    created_at: Optional[datetime] = None 