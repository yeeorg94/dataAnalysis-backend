import os
from enum import Enum
from typing import Dict, Any

# 环境类型枚举
class EnvType(str, Enum):
    DEV = "development"
    PROD = "production"
    TEST = "testing"

# 获取当前环境
def get_environment() -> str:
    """获取当前运行环境"""
    return os.getenv("APP_ENV", EnvType.DEV)

# 配置基类
class BaseConfig:
    """基础配置，所有环境通用的配置项"""
    # API 配置
    API_TITLE = "数据分析 API"
    API_DESCRIPTION = "小红书和抖音数据分析 API"
    API_VERSION = "0.1.0"
    
    # 请求头设置
    # DEFAULT_USER_AGENT = "Mozilla/5.0 (iPhone; CPU iPhone OS 16_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.6 Mobile/15E148 Safari/604.1 Edg/134.0.0.0"
    DEFAULT_USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    MOBILE_USER_AGENT = "Mozilla/5.0 (iPhone; CPU iPhone OS 16_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.6 Mobile/15E148 Safari/604.1 Edg/134.0.0.0"
    
    # 日志配置
    LOG_LEVEL = "INFO"
    LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    LOG_DATE_FORMAT = '%Y-%m-%d %H:%M:%S'
    LOG_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'logs')
    LOG_BACKUP_COUNT = 30
    # 关键词映射
    APP_TYPE_KEYWORD = {
        "xiaohongshu": ['小红书', 'xhs','xiaohongshu'],
        "douyin": ['抖音', 'douyin', 'dy'],
        "kuaishou": ['快手', 'kuaishou', 'ks'],
        "weibo": ['微博', 'weibo', 'wb']
    }

# 开发环境配置
class DevelopmentConfig(BaseConfig):
    """开发环境配置"""
    # 服务器设置
    HOST = "127.0.0.1"
    PORT = 8000
    RELOAD = True
    DEBUG = True
    
    # 日志配置
    LOG_LEVEL = "DEBUG"

# 生产环境配置
class ProductionConfig(BaseConfig):
    """生产环境配置"""
    # 服务器设置
    HOST = "0.0.0.0"  # 在生产环境中监听所有接口
    PORT = int(os.getenv("PORT", "8000"))  # 可通过环境变量设置端口
    RELOAD = False
    DEBUG = False
    
    # 日志配置
    LOG_LEVEL = "INFO"

# 测试环境配置
class TestingConfig(BaseConfig):
    """测试环境配置"""
    # 服务器设置
    HOST = "127.0.0.1"
    PORT = 8000
    RELOAD = False
    DEBUG = True
    
    # 日志配置
    LOG_LEVEL = "DEBUG"

# 配置映射
config_by_env = {
    EnvType.DEV: DevelopmentConfig,
    EnvType.PROD: ProductionConfig,
    EnvType.TEST: TestingConfig
}

# 获取当前环境的配置
def get_config() -> BaseConfig:
    """根据当前环境获取配置"""
    env = get_environment()
    return config_by_env.get(env, DevelopmentConfig)

# 当前配置实例
config = get_config() 