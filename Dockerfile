# 使用官方Python运行时作为基础镜像
FROM python:3.9-slim

# 设置工作目录
WORKDIR /app

# 设置环境变量
ENV APP_ENV=production
ENV HOST=0.0.0.0
ENV PORT=8000

# 复制requirements.txt并安装依赖
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 复制项目文件
COPY . .

# 创建日志目录
RUN mkdir -p logs

# 创建非root用户运行应用
RUN adduser --disabled-password --gecos '' appuser
RUN chown -R appuser:appuser /app
USER appuser

# 暴露端口
EXPOSE 8000

# 运行应用
CMD ["python", "start_server.py", "--env", "production", "--host", "0.0.0.0", "--port", "8000"]