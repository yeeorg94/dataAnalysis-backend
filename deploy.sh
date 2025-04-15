#!/bin/bash

# 部署脚本 - 在生产服务器上部署应用
# 使用方法: ./deploy.sh [port]

# 设置错误时退出
set -e

# 获取脚本所在目录的绝对路径
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_NAME="dataAnalysis-backend"
PARENT_DIR="$(dirname "$SCRIPT_DIR")"

# 日志颜色
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 日志函数
log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 处理配置文件
handle_config() {
    # 检查是否在生产环境
    if [ -f "/.dockerenv" ] || [ -f "/run/.containerenv" ]; then
        export DATA_ANALYSIS_ENV="production"
        log_info "Running in production environment"
        
        # 检查上级目录是否存在配置文件
        if [ -f "$PARENT_DIR/config.ini" ]; then
            log_info "Found production config file in parent directory"
            # 复制配置文件到项目目录
            cp "$PARENT_DIR/config.ini" "$SCRIPT_DIR/config.ini"
            log_info "Copied config file to project directory"
        else
            log_error "Production config file not found: $PARENT_DIR/config.ini"
            log_info "Please create config file in parent directory first"
            exit 1
        fi
    else
        export DATA_ANALYSIS_ENV="development"
        log_info "Running in development environment"
        
        # 检查项目目录是否存在配置文件
        if [ ! -f "$SCRIPT_DIR/config.ini" ]; then
            if [ -f "$SCRIPT_DIR/config.template.ini" ]; then
                cp "$SCRIPT_DIR/config.template.ini" "$SCRIPT_DIR/config.ini"
                log_warn "Created config.ini from template. Please update it with your settings."
                exit 1
            else
                log_error "Neither config.ini nor config.template.ini found in project directory!"
                exit 1
            fi
        fi
    fi
}

# 更新代码
update_code() {
    log_info "Updating code from repository..."
    cd "$SCRIPT_DIR"
    git pull
}

# 更新依赖
update_dependencies() {
    log_info "Updating dependencies..."
    cd "$SCRIPT_DIR"
    
    # 检查虚拟环境是否存在
    if [ ! -d ".venv" ]; then
        log_info "Creating virtual environment..."
        python3 -m venv .venv
    fi
    
    # 激活虚拟环境
    source .venv/bin/activate
    
    # 更新 pip
    python -m pip install --upgrade pip
    
    # 安装依赖
    pip install -r requirements.txt
}

# 重启服务
restart_service() {
    log_info "Restarting service..."
    
    # 检查是否存在旧的进程
    if [ -f "app.pid" ]; then
        OLD_PID=$(cat app.pid)
        if kill -0 "$OLD_PID" 2>/dev/null; then
            log_info "Stopping old process: $OLD_PID"
            kill "$OLD_PID"
            sleep 2
        fi
    fi
    
    # 启动新进程
    log_info "Starting new process..."
    source .venv/bin/activate
    export PYTHONPATH=$SCRIPT_DIR
    nohup python -m uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4 > app.log 2>&1 &
    echo $! > app.pid
    log_info "Service started with PID: $(cat app.pid)"
}

# 主流程
main() {
    log_info "Starting deployment for $PROJECT_NAME..."
    
    # 执行部署步骤
    handle_config
    update_code
    update_dependencies
    restart_service
    
    log_info "Deployment completed successfully!"
}

# 执行主流程
main