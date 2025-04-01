import json
from bs4 import BeautifulSoup
import httpx
from src.utils import get_kuaishou_logger, config
from src.utils.index import find_url
from src.utils.response import Response


logger = get_kuaishou_logger()


class Kuaishou:
    def __init__(self, text, type):
        self.text = text
        self.type = type
        self.url = find_url(text)
        self.description = ""
        self.video = ""
        self.image_list = []
        self.image_prefix = "https://tx2.a.kwimgs.com/"
        if not self.url:
            error_msg = f"无法从文本 '{text}' 中提取 URL"
            logger.error(error_msg)
            raise ValueError(error_msg)
        try:
            headers = {
                "User-Agent": config.MOBILE_USER_AGENT,
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
                "Accept-Language": "zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7",
                "Referer": "https://www.google.com/",
            }
            response = httpx.get(
                self.url, follow_redirects=True, headers=headers, timeout=10.0
            )
            self.html = response.text
            self.soup = BeautifulSoup(self.html, "html.parser")
            # 提取页面标题
            self.title = self.soup.title.text if self.soup.title else ""

            # 提取页面内容
            self.extract_kuaishou_data()
        except Exception as e:
            logger.error(f"获取网页基本信息失败: {e}")
            raise e

    def extract_kuaishou_data(self):
        """提取快手内容"""
        try:
            # 提取页面内容
            self.image_data = {}
            self.video_data = {}
            scripts = self.soup.find_all("script")

            for script in scripts:
                if script.string and "window.INIT_STATE" in script.string:
                    data_text = script.string.split("window.INIT_STATE = ")[1]
                    logger.info(f"提取到的数据: {data_text}")
                    # 提取出来的数据转成dict
                    data_dict = json.loads(data_text)
                    self.data_dict = data_dict
                    break
            self.get_dict_data()
        except Exception as e:
            logger.error(f"提取快手内容失败: {e}")
            raise e

    def get_dict_data(self):
        """获取dict数据"""
        try:
            data_list = list(self.data_dict.values())
            obj1_data = data_list[2] if len(data_list) > 2 else {}
            obj2_data = obj1_data.get("photo", {})
            obj3_data = obj2_data.get("manifest", {})
            obj4_data = obj2_data.get("ext_params", {})
            # 获取视频数据
            if len(obj3_data) > 0:
                self.get_video_data(obj3_data)
            # 获取图片数据
            if len(obj4_data) > 0:
                self.get_image_data(obj4_data)
            # 获取描述
            self.description = obj2_data.get("caption", "")

        except Exception as e:
            logger.error(f"获取dict数据失败: {e}")
            raise e

    def get_video_data(self, obj3_data):
        """获取视频数据"""
        try:
            adaptationSet = obj3_data.get("adaptationSet", [])
            adaptationSet_item = adaptationSet[0] if len(adaptationSet) > 0 else {}
            representation = adaptationSet_item.get("representation", [])
            representation_item = representation[0] if len(representation) > 0 else {}
            backupUrl = representation_item.get("backupUrl", [])
            self.video = backupUrl[0]
        except Exception as e:
            logger.error(f"获取视频数据失败: {e}")
            raise e

    def get_image_data(self, obj4_data):
        """获取图片数据"""
        try:
            atlas = obj4_data.get("atlas", {})
            id_list = atlas.get("list", [])
            if len(id_list) > 0:
                for item in id_list:
                    if item:
                        self.image_list.append(self.image_prefix + item)
        except Exception as e:
            logger.error(f"获取图片数据失败: {e}")
            raise e

    def to_dict(self):
        """将对象转换为字典，用于 API 返回"""
        try:
            result = {
                "url": self.url,
                "final_url": "",
                "title": self.title,
                "description": self.description,
                "image_list": self.image_list,
                "video": self.video,
                "app_type": "xiaohongshu",
            }
            return Response.success(result, "获取成功")
        except Exception as e:
            logger.error(f"转换为字典时出错: {str(e)}", exc_info=True)
            return Response.error("获取失败")
