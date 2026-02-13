FROM python:3.11-slim

WORKDIR /app

# 安装依赖
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 复制代码
COPY backend/ ./backend/
COPY config/ ./config/
COPY frontend/ ./frontend/
COPY data/ ./data/

# 暴露端口
EXPOSE 80

# 启动命令
CMD ["python3", "-m", "uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "80"]
