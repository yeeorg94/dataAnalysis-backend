# 社交媒体数据分析API

[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104.1-green.svg)](https://fastapi.tiangolo.com/)

基于FastAPI的社交媒体数据分析API服务，支持从小红书、抖音、快手、微博等平台提取和分析数据。

## 📑 功能特点

- ✅ **多平台支持**：同时支持小红书、抖音、快手、微博等主流社交媒体平台
- ✅ **数据提取**：自动解析分享链接，提取包括文字、图片、视频、用户信息等多维度数据
- ✅ **灵活输出**：支持JSON和HTML两种输出格式，适应不同应用场景
- ✅ **高性能**：采用FastAPI异步框架，支持高并发请求处理
- ✅ **安全可靠**：完善的日志记录和异常处理机制
- ✅ **易于扩展**：模块化设计，便于添加新平台支持

## 🧰 技术栈

- **Web框架**：FastAPI
- **服务器**：Uvicorn
- **数据解析**：BeautifulSoup4、lxml、Selenium
- **数据库**：MySQL (通过PyMySQL和DBUtils)
- **HTTP客户端**：Requests、httpx
- **数据处理**：Pandas

## 🏗️ 项目结构

```
.
├── main.py              # 主应用入口
├── start_server.py      # 服务启动脚本
├── deploy.sh            # 生产环境部署脚本
├── run_dev.sh           # 开发环境启动脚本
├── requirements.txt     # 依赖列表
├── config.template.ini  # 配置文件模板
├── logs/                # 日志目录
├── data/                # 数据存储目录
├── storage/             # 文件存储目录
└── src/                 # 源代码目录
    ├── app/             # 应用逻辑实现
    │   ├── xiaohongshu/ # 小红书相关实现
    │   ├── douyin/      # 抖音相关实现
    │   ├── kuaishou/    # 快手相关实现
    │   └── weibo/       # 微博相关实现
    ├── models/          # 数据模型
    ├── services/        # 业务逻辑
    ├── utils/           # 工具函数
    └── routes/          # API路由
        ├── analyze.py   # 数据分析路由
        ├── tracking.py  # 用户行为埋点路由
        └── system.py    # 系统相关路由
```

## 📝 API文档

### 主要接口

| 端点 | 方法 | 描述 |
|------|------|------|
| `/analyze` | POST | 通用数据分析接口，自动识别平台类型 |
| `/analyze/xiaohongshu` | POST | 小红书数据分析接口 |
| `/analyze/douyin` | POST | 抖音数据分析接口 |
| `/analyze/kuaishou` | POST | 快手数据分析接口 |
| `/analyze/weibo` | POST | 微博数据分析接口 |
| `/health` | GET | 健康检查接口 |

### 请求参数

```json
{
  "url": "社交媒体分享链接",
  "type": "png",  // 可选，图片类型，支持 "png" 或 "webp"
  "format": "json" // 可选，返回格式，支持 "json" 或 "html"
}
```

### 示例请求

```bash
curl -X 'POST' \
  'http://localhost:8000/analyze' \
  -H 'Content-Type: application/json' \
  -d '{
  "url": "https://www.xiaohongshu.com/explore/example",
  "type": "png",
  "format": "json"
}'
```

## 🛠️ 环境配置

项目支持两种运行环境：

- **development**: 开发环境（默认）
- **production**: 生产环境

## 📊 数据库配置

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

## 📦 安装和部署

### 开发环境

1. 克隆项目：
```bash
git clone https://github.com/yourusername/social-media-analysis-api.git
cd social-media-analysis-api
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
# 使用开发脚本
./run_dev.sh

# 或直接使用Python
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

### 作为守护进程运行

项目提供了在后台作为守护进程运行的脚本:

```bash
./run_as_daemon.sh
```

## 📝 日志管理

- 应用日志：`logs/deploy_*.log`
- 进程 ID：`logs/server.pid`

## 📚 API文档访问

服务启动后，可以通过以下URL访问API文档：

- **Swagger UI文档**: http://[host]:[port]/docs
- **ReDoc文档**: http://[host]:[port]/redoc

## 🔍 问题排查

### 常见问题及解决方案：

1. **配置文件问题**
   - 确保开发环境下 `config.ini` 在项目根目录
   - 确保生产环境下 `config.ini` 在项目父目录

2. **数据库连接问题**
   - 检查配置文件中的数据库信息是否正确
   - 确保数据库服务正在运行
   - 检查数据库用户权限

3. **服务启动问题**
   - 检查端口是否被占用
   - 查看 `logs/deploy_*.log` 中的错误信息
   - 确保所有依赖都已正确安装

4. **平台解析失败**
   - 检查URL格式是否正确
   - 确认所使用的平台是否支持
   - 查看日志了解详细错误信息

## 🧩 扩展开发

### 添加新平台支持

1. 在 `src/app` 下创建新平台目录
2. 实现平台特定的爬取和解析逻辑
3. 在 `src/routes/analyze.py` 中添加新平台的路由处理
4. 更新 `config.APP_TYPE_KEYWORD` 添加新平台关键词

## 📄 许可证

本项目采用 MIT 许可证 - 详见 [LICENSE](LICENSE) 文件

## 👨‍💻 贡献

欢迎提交 Pull Request 和 Issue!

## 📧 联系方式

如有问题或建议，请通过以下方式联系：

- **Email**: solvix@163.com
- **GitHub Issues**: [提交问题](https://github.com/yinhw0210/dataAnalysis-backend/issues) 