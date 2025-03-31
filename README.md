# 数据分析 API

一个基于 FastAPI 的数据分析 API 服务，支持小红书和抖音数据提取。

## 项目结构

```
.
├── main.py              # 主应用入口
├── start_server.py      # 服务启动脚本
├── deploy.sh            # 生产环境部署脚本
├── run_dev.sh           # 开发环境运行脚本
├── requirements.txt     # 依赖列表
├── logs/                # 日志目录
└── src/                 # 源代码目录
    ├── app/             # 应用核心模块
    │   ├── xiaohongshu/ # 小红书数据处理模块
    │   └── tiktok/      # 抖音数据处理模块
    ├── module/          # API路由模块
    │   ├── xiaohongshu/ # 小红书API路由
    │   └── routes.py    # 路由注册中心
    └── utils/           # 工具模块
        ├── config.py    # 配置管理
        ├── logger.py    # 日志管理
        └── index.py     # 工具函数
```

## 环境配置

项目支持三种运行环境：

- **development**: 开发环境（默认）
- **production**: 生产环境
- **testing**: 测试环境

通过环境变量 `APP_ENV` 设置运行环境：

```bash
export APP_ENV="production"
```

## 安装依赖

```bash
# 创建虚拟环境（如果尚未创建）
python -m venv venv

# 激活虚拟环境
source venv/bin/activate  # Linux/Mac
# 或
venv\Scripts\activate     # Windows

# 安装依赖
pip install -r requirements.txt
```

## 开发模式运行

使用 `run_dev.sh` 脚本在开发模式下运行：

```bash
./run_dev.sh [端口号]
```

或者直接使用 Python：

```bash
export APP_ENV="development"  # 设置环境
python main.py
```

## 生产环境部署

### 使用部署脚本

```bash
# 部署应用，使用默认端口 8000
./deploy.sh

# 指定端口
./deploy.sh 9000

# 指定主机和端口
./deploy.sh 9000 0.0.0.0
```

### 手动部署

1. 克隆仓库
   ```bash
   git clone <仓库地址>
   cd <项目目录>
   ```

2. 创建虚拟环境并安装依赖
   ```bash
   python -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

3. 设置环境变量并启动服务
   ```bash
   export APP_ENV="production"
   python start_server.py --env production --port 8000 --host 0.0.0.0
   ```

### 使用守护进程

可以使用 `nohup` 或 `systemd` 确保服务在后台运行：

```bash
# 使用 nohup
nohup python start_server.py --env production > logs/app.log 2>&1 &
echo $! > logs/server.pid
```

## API 端点

### 核心端点
- `GET /`: API 根端点，返回服务状态
- `GET /health`: 健康检查端点

### 小红书模块
- `GET /xiaohongshu?url=<url>`: 获取小红书数据（GET 方法）
- `POST /xiaohongshu`: 获取小红书数据（POST 方法）
- `POST /getXiaohongshu`: 获取小红书数据（向后兼容）

## 扩展新模块

项目使用模块化的设计，可以轻松添加新的API模块：

1. 在 `src/module/` 下创建新模块文件夹（如 `douyin`）
2. 创建模块的路由文件 `routes.py`
3. 在 `src/module/routes.py` 中注册新模块

## 日志

所有日志保存在 `logs` 目录下：

- `app_*.log`: 应用主日志
- `xiaohongshu_*.log`: 小红书模块日志
- `tiktok_*.log`: 抖音模块日志
- `system_*.log`: 系统日志

## 查看日志

```bash
# 查看应用日志
tail -f logs/app_$(date +"%Y-%m-%d").log

# 查看小红书模块日志
tail -f logs/xiaohongshu_$(date +"%Y-%m-%d").log
```

## API 文档

服务启动后，可以通过以下URL访问API文档：

- Swagger UI文档: http://[host]:[port]/docs
- ReDoc文档: http://[host]:[port]/redoc

## 监控与维护

### 检查服务状态

```bash
# 检查进程是否运行
ps -p $(cat logs/server.pid)

# 检查健康状态
curl http://[host]:[port]/health
```

### 重启服务

```bash
# 停止当前服务
kill $(cat logs/server.pid)

# 重新启动服务
./deploy.sh
```

## 问题排查

常见问题及解决方案：

1. **日志查看**：所有错误都记录在日志文件中，可以检查相应的日志文件
2. **端口占用**：如果端口已被占用，可以使用不同的端口启动
3. **权限问题**：确保脚本有执行权限 (`chmod +x *.sh`)
4. **依赖问题**：确保所有依赖都已正确安装 