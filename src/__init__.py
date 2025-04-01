# src 包初始化
from .app.xiaohongshu.index import Xiaohongshu
from .app.tiktok.index import Tiktok
from .app.xiaohongshu.image import Image
from .app.kuaishou.index import Kuaishou

__all__ = ["Xiaohongshu", "Image", "Tiktok"]