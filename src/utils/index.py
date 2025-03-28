import re
from typing import Optional
from .logger import get_utils_logger

__all__ = ["find_url"]

# 获取工具模块的日志器
logger = get_utils_logger()

def find_url(string: str) -> Optional[str]:
    """
    从文本中提取 URL
    
    参数:
        string: 包含 URL 的文本
        
    返回:
        提取的 URL 或 None (如果未找到)
    """
    try:
        # 如果输入就是一个 URL，直接返回
        if string.startswith(('http://', 'https://')):
            logger.info(f"输入已是URL: {string}")
            return string
            
        # 否则在文本中查找 URL
        # 将中文逗号替换为空格，以便更好地分隔
        tmp = string.replace("，", " ").replace(",", " ")
        
        # 查找 URL
        match = re.search(r"(?P<url>https?://[^\s]+)", tmp)
        if match:
            url = match.group("url")
            # 移除 URL 末尾可能的标点符号
            url = re.sub(r'[.,;:!?)]+$', '', url)
            logger.info(f"从文本中提取到URL: {url}")
            return url
        
        logger.warning(f"在文本中未找到URL: {string}")
        return None
    except Exception as e:
        logger.error(f"提取 URL 时出错: {str(e)}", exc_info=True)
        return None