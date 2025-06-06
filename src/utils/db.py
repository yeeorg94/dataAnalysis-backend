import pymysql
from dbutils.pooled_db import PooledDB
import configparser
import os
from src.utils import get_db_logger
from typing import Optional, Any, List, Dict

logger = get_db_logger()

class DatabasePool:
    _instance = None
    _config_valid = False
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(DatabasePool, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
            
        self._initialized = True
        try:
            self.config = self._load_config()
            # 只有在成功加载配置文件时才尝试创建连接池
            if self.config is not None:
                self.pool = self._create_pool()
                DatabasePool._config_valid = True
            else:
                logger.warning("No database configuration file found. Database features will be disabled.")
                DatabasePool._config_valid = False
        except Exception as e:
            logger.error(f"Error initializing database pool: {e}")
            DatabasePool._config_valid = False
            
    def _load_config(self) -> Optional[dict]:
        """加载数据库配置，如果配置文件不存在则返回None"""
        config = configparser.ConfigParser()
        
        if os.path.exists('config.ini'):
            config.read('config.ini')
            return config['mysql']
        elif os.path.exists('config.template.ini'):
            config.read('config.template.ini')
            return config['mysql']
        else:
            # 不再抛出异常，而是返回None
            logger.warning("No configuration file found (config.ini or config.template.ini)")
            return None
        
    def _create_pool(self) -> Optional[PooledDB]:
        """创建数据库连接池"""
        # 如果配置为None，则不创建连接池
        if self.config is None:
            return None
            
        try:
            pool = PooledDB(
                creator=pymysql,        # 使用链接数据库的模块
                maxconnections=6,       # 连接池允许的最大连接数
                mincached=2,            # 初始化时，链接池中至少创建的空闲的链接，0表示不创建
                maxcached=5,            # 链接池中最多闲置的链接，0和None不限制
                maxshared=3,            # 链接池中最多共享的链接数量，0和None表示全部共享
                blocking=True,          # 连接池中如果没有可用连接后，是否阻塞等待
                maxusage=None,          # 一个链接最多被重复使用的次数，None表示无限制
                setsession=[],          # 开始会话前执行的命令列表
                ping=0,                 # ping MySQL服务端，检查是否服务可用
                host=self.config['host'],
                port=int(self.config['port']),
                user=self.config['user'],
                password=self.config['password'],
                database=self.config['database'],
                charset='utf8mb4',
                cursorclass=pymysql.cursors.DictCursor
            )
            logger.info("Database connection pool created successfully")
            return pool
        except Exception as e:
            logger.error(f"Error creating database pool: {e}")
            DatabasePool._config_valid = False
            return None
            
    def get_connection(self):
        """获取数据库连接"""
        if not DatabasePool._config_valid:
            raise RuntimeError("Database is not configured properly")
        return self.pool.connection()

    @classmethod
    def is_configured(cls) -> bool:
        """检查数据库是否已正确配置"""
        return cls._config_valid

class DatabaseConnection:
    def __init__(self):
        self.pool = DatabasePool()
        self.connection = None
        self.cursor = None
        
    def __enter__(self):
        """上下文管理器入口"""
        if not DatabasePool.is_configured():
            raise RuntimeError("Database is not configured properly")
        self.connection = self.pool.get_connection()
        self.cursor = self.connection.cursor()
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        """上下文管理器出口"""
        if self.cursor:
            self.cursor.close()
        if self.connection:
            self.connection.close()
            
    def execute_query(self, query: str, params: Optional[tuple] = None) -> List[Dict[str, Any]]:
        """
        执行SQL查询
        :param query: SQL查询语句
        :param params: 查询参数
        :return: 查询结果
        """
        if not DatabasePool.is_configured():
            raise RuntimeError("Database is not configured properly")
        try:
            with self as db:
                db.cursor.execute(query, params)
                if query.strip().upper().startswith(('SELECT', 'SHOW')):
                    return db.cursor.fetchall()
                else:
                    db.connection.commit()
                    return db.cursor.rowcount
        except Exception as e:
            logger.error(f"Error executing query: {e}")
            if not query.strip().upper().startswith(('SELECT', 'SHOW')):
                if self.connection:
                    self.connection.rollback()
            raise 