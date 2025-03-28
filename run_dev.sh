#!/bin/bash

# 开发环境运行脚本
# 使用方法: ./run_dev.sh [port]

# 获取脚本所在目录的绝对路径
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
cd "$SCRIPT_DIR"

# 默认端口
PORT=${1:-8000}

# 确保日志目录存在
mkdir -p logs

# 如果存在虚拟环境，则激活
if [ -d "venv" ]; then
    echo "激活虚拟环境..."
    source venv/bin/activate
fi

# 设置环境变量
export APP_ENV="development"
export PORT="$PORT"

echo "以开发模式启动服务，端口: $PORT..."

# 直接使用 Python 启动，便于查看输出
python main.py 