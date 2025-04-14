from seleniumwire import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from src.utils import get_test_logger
from seleniumwire.request import (
    Request as SeleniumRequest,
    Response as SeleniumResponse,
)
from src.utils.response import Response
import gzip
import json

# 在原有导入基础上新增必要模块
logger = get_test_logger()


class Test:
    def __init__(self, url):
        self.url = url
        self.html = ""
        self.image_list = []
        self.body = {}
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
        # WebDriverWait(self.driver, 10).until(
        #     EC.presence_of_element_located((By.CLASS_NAME, "woo-box-flex"))
        # )

        # for request in self.driver.requests:
        #     logger.info(request.url)
        #     if 'statuses/show' in request.url:
        #         logger.info(request.response)

    def on_request(self, request: SeleniumRequest):
        if "statuses/show" in request.url:
            logger.info(request.url)

    def on_response(self, request: SeleniumRequest, response: SeleniumResponse):
        if "statuses/show" in request.url:
            body_str = gzip.decompress(response.body)
            body = json.loads(body_str)
            self.body = body
            self.get_image_list()
            
    def get_image_list(self):
        pic_ids = self.body.get("pic_ids", [])
        for pic_id in pic_ids:
            url = f"https://wx1.sinaimg.cn/osj1080/{pic_id}.jpg"
            self.image_list.append(url)
            
        return self.image_list

    def to_dict(self):
        """执行爬取流程"""
        try:
            result = {"html": self.html, "url": self.url}
            return Response.success(result, "获取成功")
        except Exception as e:
            return Response.error("获取失败")
        finally:
            # self.driver.quit()
            pass
