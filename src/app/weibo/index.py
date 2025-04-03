# 无头模式爬取微博内容
import selenium
from selenium import webdriver

class Weibo:
    def __init__(self, url):
        self.url = url
        self.driver = webdriver.Chrome()

    def get_content(self):
        self.driver.get(self.url)
        return self.driver.page_source
