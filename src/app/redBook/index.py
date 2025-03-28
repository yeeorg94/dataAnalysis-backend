from src.utils import find_url, get_redbook_logger, config
import re
import httpx
from bs4 import BeautifulSoup
import json

# 获取小红书模块的日志器
logger = get_redbook_logger()

class RedBook:
    def __init__(self, text):
        try:
            self.text = text
            self.url = find_url(text)
            
            if not self.url:
                error_msg = f"无法从文本 '{text}' 中提取 URL"
                logger.error(error_msg)
                raise ValueError(error_msg)
            
            # 获取重定向 URL
            try:
                logger.info(f"开始获取URL内容: {self.url}")
                headers = {
                    'User-Agent': config.DEFAULT_USER_AGENT,
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
                    'Accept-Language': 'zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7',
                    'Referer': 'https://www.google.com/'
                }
                
                response = httpx.get(self.url, follow_redirects=True, headers=headers, timeout=10.0)
                self.final_url = response.url
                self.html = response.text
                logger.info(f"成功获取URL内容: {self.url} -> {self.final_url}")
                
                # 使用 BeautifulSoup 解析 HTML
                self.soup = BeautifulSoup(self.html, 'html.parser')
                
                # 提取页面标题
                self.title = self.soup.title.text if self.soup.title else ""
                logger.info(f"页面标题: {self.title}")
                
                # 尝试提取小红书数据（示例）
                self.extract_redbook_data()
                
            except Exception as e:
                logger.error(f"获取 URL 内容时出错: {str(e)}", exc_info=True)
                self.final_url = None
                self.html = ""
                self.soup = None
                self.title = ""
                self.data = {}
                
        except Exception as e:
            logger.error(f"RedBook 初始化错误: {str(e)}", exc_info=True)
            # 设置一些默认值，避免后续处理出错
            self.url = None
            self.final_url = None
            self.html = ""
            self.soup = None
            self.title = ""
            self.data = {}
    
    def extract_redbook_data(self):
        """尝试从 HTML 中提取小红书数据"""
        try:
            self.data = {}
            
            # 尝试查找包含 JSON 数据的脚本标签
            scripts = self.soup.find_all('script')
            for script in scripts:
                # 查找可能包含数据的脚本内容
                if script.string and 'window.__INITIAL_STATE__' in script.string:
                    try:
                        # logger.info(f"提取到了关键词{script}")
                        # 提取 JSON 数据
                        data_text = script.string.split('window.__INITIAL_STATE__=')[1]
                        try:
                            self.data = json.loads(data_text)
                            logger.info("成功从脚本标签中提取数据")
                        except json.JSONDecodeError as e:
                            logger.error(f"JSON 格式错误: {str(e)}")
                        break
                    except:
                        continue
            
            # 如果没有找到数据，尝试直接从 HTML 中提取一些基本信息
            if not self.data:
                logger.warning("未从脚本标签中找到数据，将提取基本信息")
                # 提取一些基本信息作为备用
                self.data = {
                    "title": self.title,
                    "meta_description": self.get_meta_description(),
                    "images": self.get_all_images()
                }
                
        except Exception as e:
            logger.error(f"提取数据时出错: {str(e)}", exc_info=True)
            self.data = {"error": str(e)}
    
    def get_meta_description(self):
        """获取页面的元描述"""
        try:
            meta = self.soup.find('meta', attrs={'name': 'description'}) or self.soup.find('meta', attrs={'property': 'og:description'})
            description = meta.get('content', '') if meta else ''
            logger.debug(f"元描述: {description[:50]}...")
            return description
        except Exception as e:
            logger.error(f"获取元描述时出错: {str(e)}")
            return ''
    
    def get_all_images(self):
        """获取页面中的所有图片 URL"""
        try:
            images = [img.get('src') for img in self.soup.find_all('img') if img.get('src')]
            logger.debug(f"找到 {len(images)} 张图片")
            return images
        except Exception as e:
            logger.error(f"获取图片时出错: {str(e)}")
            return []
    
    def get_html(self, url):
        """
        获取 URL 的 HTML 内容
        """
        try:
            if url is None:
                logger.warning("URL为None，无法获取HTML")
                return ""
                
            if isinstance(url, re.Match):
                # 如果是匹配对象，获取第一个分组
                url = url.group(1) if url.groups() else ""

            logger.info(f"开始获取HTML内容: {url}")
            headers = {
                'User-Agent': config.DEFAULT_USER_AGENT,
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8'
            }
            
            response = httpx.get(url, follow_redirects=True, headers=headers, timeout=10.0)
            logger.info(f"成功获取HTML内容，长度: {len(response.text)}")
            return response.text
        except Exception as e:
            logger.error(f"获取 HTML 内容出错: {str(e)}", exc_info=True)
            return ""
            
    def to_dict(self):
        """将对象转换为字典，用于 API 返回"""
        try:
            logger.info(f"转换为字典: {type(self.data)}")
            note_data = self.data['noteData']['data']['noteData']
            image_list = []
            for image in note_data['imageList']:
                image_list.append(image['url'])
            result = {
                "data": {
                    "url": self.url,
                    "final_url": str(self.final_url) if self.final_url else None,
                    "title": self.title,
                    "description":note_data['desc'],
                    "image_list": image_list
                }
            }
            return result
        except Exception as e:
            logger.error(f"转换为字典时出错: {str(e)}", exc_info=True)
            return {}