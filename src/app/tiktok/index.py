from logging import config

from src.utils.index import find_url


class Tiktok:
    def __init__(self, text, type):
        self.text = text
        self.type = type
        self.app_type_keyword = config.APP_TYPE_KEYWORD.get('tiktok')
        self.url = find_url(text)
        
    def to_dict(self):
        return {
            'text': self.text,
            'type': self.type,
            'url': self.url
        }
