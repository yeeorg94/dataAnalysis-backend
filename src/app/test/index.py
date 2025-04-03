import json
from seleniumwire import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from urllib.parse import urlparse
import time
from src.utils import get_test_logger
from src.utils.response import Response

# 在原有导入基础上新增必要模块
logger = get_test_logger()


class Test:
    def __init__(self, url):
        self.url = url
        self.html = ""
        self._init_driver()

    def _init_driver(self):
        options = {
            "request_storage": "memory",  # 仅在内存中存储请求/响应
            "request_storage_max_size": 100,  # 设置请求/响应存储的最大数量
        }
        """初始化无头浏览器配置"""
        chrome_options = Options()
        # chrome_options.add_argument("--headless=new")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_experimental_option("detach", True)
        chrome_options.add_argument(
            "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36"
        )
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        driver = webdriver.Chrome(options=chrome_options, seleniumwire_options=options)
        driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
            "source": """
            Object.defineProperty(navigator, 'webdriver', {
            get: () => undefined
            })
        """
        })
        driver.set_page_load_timeout(30)
        driver.set_script_timeout(30)
        logger.info(f"初始化浏览器: {driver}")
        self.driver = driver
        try:
            logger.info(f"开始请求: {self.url}")
            self.driver.get(self.url)
            logger.info(f"请求完成: {self.url}")
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            logger.info(f"页面加载完成: {self.url}")
            logger.info(f"请求数: {len(self.driver.requests)}")
            for request in self.driver.requests:
                # 查看接口是否包含 qrcodeServer/hxqr
                if "qrcodeServer/hxqr" in request.url:
                    logger.info(f"监听到请求: {request.url}，请求参数: {request.params}，响应: {request.response}")

        except Exception as e:
            logger.error(f"监听请求失败: {str(e)}")
        finally:
            # self.driver.quit()
            pass

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
