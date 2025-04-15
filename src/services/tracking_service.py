import json
import ipaddress
from src.utils.db import DatabaseConnection
from src.models.tracking import TrackingEvent
from src.utils import get_test_logger
from typing import List, Optional

logger = get_test_logger()

class TrackingService:
    def __init__(self):
        self.db = DatabaseConnection()
    
    def _convert_ip_to_binary(self, ip: str) -> bytes:
        """
        将IP地址转换为二进制格式
        支持IPv4和IPv6
        """
        try:
            if not ip:
                return None
            ip_obj = ipaddress.ip_address(ip)
            return ip_obj.packed
        except Exception as e:
            logger.error(f"Invalid IP address: {ip}, error: {e}")
            return None
            
    def track_event(self, event: TrackingEvent) -> bool:
        """
        记录埋点事件
        :param event: 埋点事件对象
        :return: 是否成功
        """
        try:
            query = """
                INSERT INTO event_tracking 
                (user_id, source_platform, event_type, ip_address, 
                user_agent, referrer, event_params)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """
            
            params = (
                event.user_id,
                event.source_platform.value,
                event.event_type,
                event.ip_address,
                event.user_agent,
                event.referrer,
                json.dumps(event.event_params)
            )
            
            
            result = self.db.execute_query(query, params)
            return result > 0
            
        except Exception as e:
            logger.error(f"Failed to track event: {e}")
            return False
            
    def get_events(self, 
                   event_type: Optional[str] = None,
                   source_platform: Optional[str] = None,
                   user_id: Optional[int] = None,
                   limit: int = 100) -> List[dict]:
        """
        获取埋点事件列表
        :param event_type: 事件类型（可选）
        :param source_platform: 来源平台（可选）
        :param user_id: 用户ID（可选）
        :param limit: 限制返回数量
        :return: 事件列表
        """
        try:
            query = """
                SELECT 
                    id,
                    user_id,
                    source_platform,
                    event_type,
                    INET6_NTOA(ip_address) as ip_address,
                    user_agent,
                    referrer,
                    event_params,
                    created_at
                FROM event_tracking
                WHERE 1=1
            """
            params = []
            
            if event_type:
                query += " AND event_type = %s"
                params.append(event_type)
                
            if source_platform:
                query += " AND source_platform = %s"
                params.append(source_platform)
                
            if user_id:
                query += " AND user_id = %s"
                params.append(user_id)
                
            query += " ORDER BY created_at DESC LIMIT %s"
            params.append(limit)
            
            events = self.db.execute_query(query, tuple(params))
            
            # 转换JSON字符串为字典
            for event in events:
                if isinstance(event['event_params'], str):
                    event['event_params'] = json.loads(event['event_params'])
                    
            return events
            
        except Exception as e:
            logger.error(f"Failed to get events: {e}")
            return [] 