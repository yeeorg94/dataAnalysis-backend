# src 包初始化
from .app.xiaohongshu.index import Xiaohongshu
from .app.tiktok.index import Tiktok
from .app.xiaohongshu.image import Image
from .app.kuaishou.index import Kuaishou
from .app.test.index import Test
from .app.weibo.index import Weibo

__all__ = ["Xiaohongshu", "Image", "Tiktok", "Test", "Weibo"]