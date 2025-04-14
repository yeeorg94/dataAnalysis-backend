from seleniumwire import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from src.utils import get_weibo_logger
from seleniumwire.request import (
    Request as SeleniumRequest,
    Response as SeleniumResponse,
)
from src.utils.response import Response
import gzip
import json

logger = get_weibo_logger()

class Weibo:
    def __init__(self, url, type):
        self.url = url
        self.type = type
        self.html = ""
        self.image_list = []
        self.body = {}
        self.title = ""
        self.description = ""
        self.video = ""
        self.app_type = "weibo"
        self._init_driver()

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
        
        logger.info('页面加载完成')

    def on_request(self, request: SeleniumRequest):
        if "statuses/show" in request.url:
            import time
            time.sleep(2)

    def on_response(self, request: SeleniumRequest, response: SeleniumResponse):
        if "statuses/show" in request.url:
            body_str = gzip.decompress(response.body)
            logger.info(body_str,'body_str')
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
                "video": self.video,
                "app_type": self.app_type,
            }
            return Response.success(result, "获取成功")
        except Exception as e:
            logger.error(f"转换为字典时出错: {str(e)}", exc_info=True)
            return Response.error("获取失败")
