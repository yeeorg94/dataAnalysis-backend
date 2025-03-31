
import json
from bs4 import BeautifulSoup
import httpx
from src.utils import get_tiktok_logger, config
from src.utils.index import find_url


logger = get_tiktok_logger()
class Tiktok:
    def __init__(self, text, type):
        self.text = text
        self.type = type
        self.url = find_url(text)
        if not self.url:
                error_msg = f"无法从文本 '{text}' 中提取 URL"
                logger.error(error_msg)
                raise ValueError(error_msg)
        try:
            headers = {
                'User-Agent': config.MOBILE_USER_AGENT,
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
                'Accept-Language': 'zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7',
                'Referer': 'https://www.google.com/'
            }
            response = httpx.get(self.url, follow_redirects=True, headers=headers, timeout=10.0)
            self.html = response.text
            self.soup = BeautifulSoup(self.html, 'html.parser')
            # 提取页面标题
            self.title = self.soup.title.text if self.soup.title else ""
            
            # 提取页面内容
            self.extract_tiktok_data()
        except Exception as e:
            logger.error(f"获取抖音内容失败: {e}")
            raise e
        
    def extract_tiktok_data(self):
        """提取抖音内容"""
        try:
            # 提取页面内容
            self.image_data = {}
            self.video_data = {}
            scripts = self.soup.find_all('script')
            # logger.info(f"提取到的脚本: {scripts}")
            
            for script in scripts:
                if script.string and 'window._ROUTER_DATA' in script.string:
                    data_text = script.string.split('window._ROUTER_DATA = ')[1]
                    # logger.info(f"提取到的数据: {type(data_text)}")
                    # 判断有没有note_(id)/page, 没有的话取video_(id)/page
                    # logger.info(f"data_text: {json.loads(data_text)['loaderData']}")
                    if 'note_(id)' in data_text:
                        item_list = json.loads(data_text)['loaderData']['note_(id)/page']['videoInfoRes']['item_list']
                    else:
                        item_list = json.loads(data_text)['loaderData']['video_(id)/page']['videoInfoRes']['item_list']
                    self.description = item_list[0]['desc']
                    self.image_data = item_list[0]['images']
                    self.video_data = item_list[0]['video']
                    break
        except Exception as e:
            logger.error(f"提取抖音内容失败: {e}")
            raise e

    def to_dict(self):
        """将对象转换为字典，用于 API 返回"""
        try:
            image_list = []
            for item in self.image_data if self.image_data else []:
                image_list.append(item['url_list'][0])
                
            video = self.video_data['play_addr']['url_list'][0] if self.video_data else ''
            result = {
                "data": {
                    "url": self.url,
                    "final_url": '',
                    "title": self.title,
                    "description":self.description,
                    "image_list": image_list,
                    "video": video,
                    "app_type": 'xiaohongshu'
                }
            }
            return result
        except Exception as e:
            logger.error(f"转换为字典时出错: {str(e)}", exc_info=True)
            return {}
