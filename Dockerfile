# 使用Python3.9 slim基础镜像
FROM python:3.9-slim

# 设置工作目录
WORKDIR /app

# 设置环境变量
ENV APP_ENV=production
ENV HOST=0.0.0.0
ENV PORT=8000
ENV PYTHONPATH=/app
ENV PIP_NO_CACHE_DIR=1
ENV PIP_DISABLE_PIP_VERSION_CHECK=1

# 一次性安装所有系统依赖和Python包，然后清理
COPY requirements.txt .
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    curl \
    pkg-config \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender1 \
    libgomp1 \
    libglib2.0-dev \
    libgl1-mesa-glx \
    && pip install --no-cache-dir -r requirements.txt \
    && apt-get purge -y gcc g++ pkg-config libglib2.0-dev \
    && apt-get autoremove -y \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/* /root/.cache/pip

# 复制项目文件（.dockerignore会排除不需要的文件）
COPY . .

# 创建必要目录
RUN mkdir -p logs storage

# 创建非root用户
RUN adduser --disabled-password --gecos '' appuser \
    && chown -R appuser:appuser /app
USER appuser

# 暴露端口
EXPOSE 8000

# 运行应用
CMD ["python", "start_server.py", "--env", "production", "--host", "0.0.0.0", "--port", "8000"]