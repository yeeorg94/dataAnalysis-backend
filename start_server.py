#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
启动脚本 - 使用静默方式启动 API 服务，将所有日志写入文件
支持通过环境变量 APP_ENV 设置运行环境:
- development: 开发环境 (默认)
- production: 生产环境
- testing: 测试环境
"""

import os
import sys
import uvicorn
import logging
import argparse

# 添加项目根目录到 Python 路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# 解析命令行参数
def parse_args():
    parser = argparse.ArgumentParser(description='启动数据分析 API 服务')
    parser.add_argument(
        '--env', 
        choices=['development', 'production', 'testing'],
        default=os.getenv('APP_ENV', 'development'),
        help='运行环境 (默认: development)'
    )
    parser.add_argument(
        '--port',
        type=int,
        default=int(os.getenv('PORT', '8000')),
        help='服务端口 (默认: 8000)'
    )
    parser.add_argument(
        '--host',
        default=os.getenv('HOST', '127.0.0.1'),
        help='绑定主机 (默认: 127.0.0.1)'
    )
    return parser.parse_args()

# 导入日志配置
from src.utils.logger import configure_root_logger, get_app_logger
from src.utils import EnvType

# 设置环境变量
def set_environment(env):
    """设置环境变量"""
    os.environ['APP_ENV'] = env
    return env

# 获取应用日志器
def start_server():
    """静默启动服务"""
    # 解析命令行参数
    args = parse_args()
    
    # 设置环境变量
    env = set_environment(args.env)
    
    # 在导入配置前设置好环境变量
    from src.utils import config, get_app_logger
    
    # 获取日志器
    logger = get_app_logger()
    
    try:
        # 配置根日志器，确保所有日志都写入文件
        configure_root_logger()
        
        # 关闭标准输出的日志记录，将所有输出重定向到文件
        logging.getLogger("uvicorn").handlers = []
        logging.getLogger("uvicorn.access").handlers = []
        logging.getLogger("uvicorn.error").handlers = []
        
        # 设置这些日志器使用我们的日志器
        logging.getLogger("uvicorn").parent = logging.getLogger("app")
        logging.getLogger("uvicorn.access").parent = logging.getLogger("app")
        logging.getLogger("uvicorn.error").parent = logging.getLogger("app")
        
        # 使用命令行参数覆盖配置中的主机和端口
        host = args.host or config.HOST
        port = args.port or config.PORT
        
        # 记录启动信息
        logger.info(f"正在启动 API 服务... 环境: {env}, 主机: {host}, 端口: {port}")
        
        # 启动 uvicorn 服务器
        uvicorn.run(
            "main:app",                 # 应用导入字符串
            host=host,                  # 绑定的主机
            port=port,                  # 绑定的端口
            reload=False,               # 在生产环境中禁用自动重载
            log_level=config.LOG_LEVEL.lower(),  # 日志级别
            workers=1,                  # 工作进程数
            log_config=None,            # 禁用 uvicorn 默认日志配置
            access_log=False,           # 禁用 uvicorn 访问日志
        )
    except Exception as e:
        # 在出错时尝试获取日志器
        try:
            logger.error(f"启动服务时出错: {str(e)}", exc_info=True)
        except:
            # 如果日志器不可用，则在控制台输出
            print(f"启动服务时出错: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    start_server() 