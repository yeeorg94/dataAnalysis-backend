# 数据分析 API

一个基于 FastAPI 的数据分析 API 服务，支持小红书和抖音数据提取。

## 项目结构

```
.
├── main.py              # 主应用入口
├── start_server.py      # 服务启动脚本
├── deploy.sh            # 生产环境部署脚本
├── requirements.txt     # 依赖列表
├── config.template.ini  # 配置文件模板
├── logs/               # 日志目录
└── src/                # 源代码目录
    ├── models/         # 数据模型
    ├── services/       # 业务逻辑
    ├── utils/          # 工具函数
    └── routes/         # API路由
```

## 环境配置

项目支持两种运行环境：

- **development**: 开发环境（默认）
- **production**: 生产环境

## 数据库配置

### 配置文件说明

项目使用 `config.ini` 进行数据库配置：

- 开发环境：配置文件位于项目根目录
- 生产环境：配置文件位于项目父目录（部署时会自动复制到项目目录）

配置文件格式：
```ini
[mysql]
host = localhost
port = 3306
user = your_username
password = your_password
database = your_database
```

### 数据库连接池

项目使用 PyMySQL 和 DBUtils 实现数据库连接池，特性包括：
- 自动管理连接池大小
- 支持连接自动回收
- 支持连接健康检查

使用示例：
```python
from src.utils.db import DatabaseConnection

with DatabaseConnection() as db:
    result = db.execute_query("SELECT * FROM your_table")
```

## 安装和部署

### 开发环境

1. 克隆项目：
```bash
git clone [repository_url]
cd dataAnalysis-backend
```

2. 创建并激活虚拟环境：
```bash
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# 或
.venv\Scripts\activate  # Windows
```

3. 安装依赖：
```bash
pip install -r requirements.txt
```

4. 配置数据库：
```bash
cp config.template.ini config.ini
# 编辑 config.ini 填入正确的数据库配置
```

5. 启动开发服务器：
```bash
python start_server.py
```

### 生产环境

1. 在项目父目录创建并配置 `config.ini`

2. 运行部署脚本：
```bash
chmod +x deploy.sh
./deploy.sh [port] [host]  # 端口和主机地址可选，默认为 8000 和 0.0.0.0
```

部署脚本会自动：
- 复制父目录的配置文件到项目目录
- 创建/激活虚拟环境
- 更新代码（git pull）
- 安装/更新依赖
- 重启服务

## 日志

- 应用日志：`logs/deploy_*.log`
- 进程 ID：`logs/server.pid`

## API 文档

服务启动后，可以通过以下URL访问API文档：

- Swagger UI文档: http://[host]:[port]/docs
- ReDoc文档: http://[host]:[port]/redoc

## 问题排查

常见问题及解决方案：

1. 配置文件问题
   - 确保开发环境下 `config.ini` 在项目根目录
   - 确保生产环境下 `config.ini` 在项目父目录

2. 数据库连接问题
   - 检查配置文件中的数据库信息是否正确
   - 确保数据库服务正在运行
   - 检查数据库用户权限

3. 服务启动问题
   - 检查端口是否被占用
   - 查看 `logs/deploy_*.log` 中的错误信息
   - 确保所有依赖都已正确安装 