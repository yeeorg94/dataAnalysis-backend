from src.app.xiaohongshu.image import Image
from src.utils import find_url, get_analyze_logger, config, Response
import re
import httpx
from bs4 import BeautifulSoup
import json

# 获取小红书模块的日志器
logger = get_analyze_logger()

class Xiaohongshu:
    def __init__(self, text, type):
        try:
            self.text = text
            self.url = find_url(text)
            self.type = type
            self.video = ""
            self.image_list = []
            self.live_list = []
            self.description = ""
            self.final_url = None
            self.html = ""
            self.soup = None
            self.title = ""
            self.data = {}
            self.app_type_keyword = config.APP_TYPE_KEYWORD.get("xiaohongshu")
            if not self.url:
                error_msg = f"无法从文本 '{text}' 中提取 URL"
                raise ValueError(error_msg)

            # 获取重定向 URL
            headers = {
                "User-Agent": config.DEFAULT_USER_AGENT,
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
                "Accept-Language": "zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7",
                "Referer": "https://www.google.com/",
            }

            response = httpx.get(
                self.url, follow_redirects=True, headers=headers, timeout=10.0
            )
            self.final_url = response.url
            if "404" in str(self.final_url):
                # 抛出异常
                raise ValueError(f"小红书链接已失效: {self.final_url}")
            self.html = response.text
            # 使用 BeautifulSoup 解析 HTML
            self.soup = BeautifulSoup(self.html, "html.parser")
            # 提取页面标题
            self.title = self.soup.title.text if self.soup.title else ""
            # 尝试提取小红书数据（示例）
            self.extract_xiaohongshu_data()
            
        except Exception as e:
            logger.error(f"Xiaohongshu 初始化错误: {str(e)}", exc_info=True)
            raise e
            # 设置一些默认值，避免后续处理出错

    def extract_xiaohongshu_data(self):
        """尝试从 HTML 中提取小红书数据"""
        self.data = {}
        # 尝试查找包含 JSON 数据的脚本标签
        scripts = self.soup.find_all("script")
        for script in scripts:
            # 查找可能包含数据的脚本内容
            if script.string and "window.__INITIAL_STATE__" in script.string:
                try:
                    # 提取 JSON 数据
                    data_text = script.string.split("window.__INITIAL_STATE__=")[1]
                    # 把字符串中的undefined替换为null
                    data_text = data_text.replace("undefined", "null")
                    try:
                        self.data_dict = json.loads(data_text)
                        self.get_image_list()
                        self.get_video()
                        self.get_meta_description()
                    except json.JSONDecodeError as e:
                        raise e
                    break
                except Exception as e:
                    raise e

    def get_meta_description(self):
        """获取页面的元描述"""
        meta = self.soup.find(
            "meta", attrs={"name": "description"}
        ) or self.soup.find("meta", attrs={"property": "og:description"})
        description = meta.get("content", "") if meta else ""
        self.description = description

    def get_image_list(self):
        """获取图片列表"""
        try:
            note = self.data_dict.get("note", {})
            note_detail_map = note.get("noteDetailMap", {})
            first_note_id = note.get("firstNoteId", "")
            note_data = note_detail_map.get(first_note_id, {}).get("note", {})
            image_list = note_data.get("imageList", [])
            token_list = []
            for image in image_list:
                if image.get("urlDefault"):
                    token_list.append(image.get("urlDefault", ""))
                live_url = image.get("stream", {}).get("h264", [{}])[0].get("masterUrl")
                if live_url:
                    self.live_list.append(live_url)
            self.image_list = Image(token_list, self.type).to_dict()
        except Exception as e:
            raise e

    def get_video(self):
        """获取视频"""
        try:
            note = self.data_dict.get("note", {})
            note_detail_map = note.get("noteDetailMap", {})
            first_note_id = note.get("firstNoteId", "")
            note_data = note_detail_map.get(first_note_id, {}).get("note", {})
            video_info = note_data.get("video", {}).get("media", {})
            masterUrl = (
                video_info.get("stream", {}).get("h264", [{}])[0].get("masterUrl")
            )
            self.video = masterUrl
        except Exception as e:
            raise e

    def to_dict(self):
        """将对象转换为字典，用于 API 返回"""
        try:
            result = {
                "url": self.url,
                "final_url": str(self.final_url) if self.final_url else None,
                "title": self.title,
                "description": self.description,
                "image_list": self.image_list,
                "live_list": self.live_list,
                "video": self.video,
                "app_type": "xiaohongshu",
            }
            return Response.success(result, "获取成功")
        except Exception as e:
            raise ValueError(f"小红书转换为字典时出错: {str(e)}")
