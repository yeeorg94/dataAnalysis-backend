# 多阶段构建：构建阶段
FROM python:3.9-slim AS builder

# 安装构建时需要的系统依赖
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    pkg-config \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# 设置工作目录
WORKDIR /app

# 复制requirements.txt并安装Python依赖到用户目录
COPY requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

# 生产阶段：运行时镜像
FROM python:3.9-slim

# 安装运行时必需的系统依赖
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    ca-certificates \
    libgomp1 \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# 设置工作目录
WORKDIR /app

# 设置环境变量
ENV APP_ENV=production
ENV HOST=0.0.0.0
ENV PORT=8000
ENV PYTHONPATH=/app
ENV PATH=/root/.local/bin:$PATH

# 从构建阶段复制Python包
COPY --from=builder /root/.local /root/.local

# 复制项目文件（.dockerignore会自动排除不需要的文件）
COPY . .

# 创建必要目录
RUN mkdir -p logs storage

# 创建非root用户运行应用
RUN adduser --disabled-password --gecos '' appuser \
    && chown -R appuser:appuser /app
USER appuser

# 暴露端口
EXPOSE 8000

# 健康检查
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# 运行应用
CMD ["python", "start_server.py", "--env", "production", "--host", "0.0.0.0", "--port", "8000"]