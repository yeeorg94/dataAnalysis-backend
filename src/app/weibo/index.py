from bs4 import BeautifulSoup
import execjs
import httpx
from seleniumwire import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from src.utils import config, get_analyze_logger
from seleniumwire.request import (
    Request as SeleniumRequest,
    Response as SeleniumResponse,
)
from src.utils.response import Response
import gzip
import json

logger = get_analyze_logger()


class Weibo:
    def __init__(self, url, type):
        self.url = url
        self.type = type
        self.html = ""
        self.soup = ""
        self.image_list = []
        self.live_list = []
        self.body = {}
        self.title = ""
        self.description = ""
        self.video = ""
        self.app_type = "weibo"
        # self._init_driver()
        self._init_request()

    # request方案
    def _init_request(self):
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

            # 提取页面内容
            self.extract_weibo_data()
        except Exception as e:
            logger.error(f"获取微博内容失败: {e}")
            raise e

    def extract_weibo_data(self):
        scripts = self.soup.find_all("script")
        for script in scripts:
            if script.string and "$render_data" in script.string:
                # 获取script标签里面 $render_data 的值
                js_code = f"""
                {script.string}
                function get_render_data() {{
                    return $render_data;
                }}
                """
                # 执行js代码
                ctx = execjs.compile(js_code)
                # 双引号的数据需要转换为单引号
                render_data = ctx.call("get_render_data")
                self.body = render_data.get("status", {})
                self.get_image_list()
                self.get_live_list()
                self.get_video()
                self.get_title()
                self.get_description()
                break

    # 无头浏览器方案
    def _init_driver(self):
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_argument("--disable-css-images")
        seleniumwire_options = {
            "verify_ssl": False,  # 不验证证书
            "enable_logging": True,
            "request_storage": "memory",  # 缓存到内存
            # "request_storage_base_dir": request_storage_base_dir,  # 设置请求缓存的目录
            "request_storage_max_size": 100,  # Store no more than 100 requests in memory
        }

        self.driver = webdriver.Chrome(
            options=chrome_options, seleniumwire_options=seleniumwire_options
        )

        self.driver.execute_cdp_cmd(
            "Page.addScriptToEvaluateOnNewDocument",
            {
                "source": "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"
            },
        )

        self.driver.execute_cdp_cmd("Network.enable", {})

        self.driver.request_interceptor = self.on_request
        self.driver.response_interceptor = self.on_response

        self.driver.get(self.url)

        # 等待页面出现 woo-box-flex 这个类名
        WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "woo-box-flex"))
        )

    def on_request(self, request: SeleniumRequest):
        if "statuses/show" in request.url:
            import time

            time.sleep(2)

    def on_response(self, request: SeleniumRequest, response: SeleniumResponse):
        if "statuses/show" in request.url:
            body_str = gzip.decompress(response.body)
            logger.info(body_str, "body_str")
            body = json.loads(body_str)
            self.body = body
            self.get_image_list()
            self.get_title()
            self.get_description()
            self.driver.quit()

    def get_image_list(self):
        pic_ids = self.body.get("pic_ids", [])
        for pic_id in pic_ids:
            url = f"https://wx1.sinaimg.cn/osj1080/{pic_id}.jpg"
            self.image_list.append(url)
        return self.image_list

    def get_title(self):
        title = self.body.get("text", "")
        self.title = title
        return self.title

    def get_live_list(self):
        pics = self.body.get("pics", "")
        for pic in pics:
            if pic.get("type") == "livephoto":
                self.live_list.append(pic.get("videoSrc"))
        return self.live_list

    def get_video(self):
        page_info = self.body.get("page_info", {})
        page_info_type = page_info.get("type", "")
        if page_info_type == "video":
            self.video = page_info.get("media_info", {}).get("stream_url", "")
        return self.video

    def get_description(self):
        description = self.body.get("text", "")
        self.description = description
        return self.description

    def to_dict(self):
        """将对象转换为字典，用于 API 返回"""
        try:
            result = {
                "url": self.url,
                "final_url": "",
                "title": self.title,
                "description": self.description,
                "image_list": self.image_list,
                "live_list": self.live_list,
                "video": self.video,
                "app_type": self.app_type,
            }
            return Response.success(result, "获取成功")
        except Exception as e:
            logger.error(f"微博转换为字典时出错: {str(e)}", exc_info=True)
            return Response.error("获取失败")
