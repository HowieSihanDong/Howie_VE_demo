from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
import mysql.connector
import os
import redis
import json
from dotenv import load_dotenv
# 引入已经验证成功的 AI 服务
from llm_service import get_sql_from_llm

# 加载环境变量
env_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'config', '.env')
load_dotenv(env_path)

app = FastAPI()

# 1. 允许跨域请求（确保前端 index.html 能正常访问）
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# 2. MySQL 数据库配置
DB_CONFIG = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'port': int(os.getenv('DB_PORT', 3306)),
    'user': os.getenv('DB_USER', 'root'),
    'password': os.getenv('DB_PASSWORD', ''),
    'database': os.getenv('DB_NAME', 'demo_db'),
    'charset': 'utf8mb4'
}

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FRONTEND_DIR = os.path.join(BASE_DIR, "frontend")
print(f"📌 MySQL 数据库配置: {DB_CONFIG['host']}:{DB_CONFIG['port']}/{DB_CONFIG['database']}")

# 3. 初始化 Redis 连接
try:
    redis_client = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)
    # 测试连接
    redis_client.ping()
    print("✅ Redis 已连接，缓存功能已开启")
except Exception as e:
    print(f"⚠️ Redis 未连接 (可能未启动)，将使用内存 Mock 缓存: {e}")
    redis_client = None

# 内存 Mock 缓存（如果 Redis 没启动，程序也不会崩）
mock_cache = {}

class QueryRequest(BaseModel):
    prompt: str

def get_db_connection():
    """获取 MySQL 数据库连接"""
    return mysql.connector.connect(**DB_CONFIG)

@app.post("/ask")
async def ask_ai_and_query(request: QueryRequest):
    """
    处理前端请求的主接口，增加 Redis 缓存逻辑
    """
    prompt = request.prompt.strip()
    print(f"\n[收到请求] 用户问: {prompt}")
    
    # --- Redis 缓存查找 ---
    cache_hit = False
    sql = None
    
    if redis_client:
        try:
            sql = redis_client.get(f"cache:{prompt}")
            if sql:
                cache_hit = True
                print(f"🚀 [Redis 命中] 从缓存读取 SQL")
        except Exception:
            pass
    elif prompt in mock_cache:
        sql = mock_cache[prompt]
        cache_hit = True
        print(f"📦 [Mock 缓存命中] 从内存读取 SQL")

    # --- 如果没命中缓存，才调用 AI ---
    if not sql:
        print("🤖 [AI 调用] 正在生成 SQL...")
        sql = get_sql_from_llm(prompt)
        
        # 存入缓存（有效期 1 小时）
        if redis_client:
            try:
                redis_client.setex(f"cache:{prompt}", 3600, sql)
            except Exception:
                pass
        else:
            mock_cache[prompt] = sql

    print(f"[最终 SQL] {sql}")
    
    # 第二步：执行 SQL 并查询 MySQL 数据库
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute(sql)
        rows = cursor.fetchall()
        cursor.close()
        conn.close()
        
        return {
            "status": "success",
            "sql": sql,
            "data": rows,
            "cache_hit": cache_hit # 告诉前端是否命中了缓存
        }
    except Exception as e:
        print(f"❌ 数据库查询失败: {e}")
        return {
            "status": "error",
            "sql": sql,
            "message": str(e),
            "data": [],
            "cache_hit": False
        }

# 3. 托管前端静态文件
# 这一步非常重要：它让后端同时也变成一个 Web 服务器
app.mount("/", StaticFiles(directory=FRONTEND_DIR, html=True), name="frontend")

@app.get("/")
async def read_index():
    return FileResponse(os.path.join(FRONTEND_DIR, 'index.html'))

import socket

def find_available_port(start_port: int, max_attempts: int = 10):
    """
    尝试从 start_port 开始寻找一个可用的端口
    """
    for port in range(start_port, start_port + max_attempts):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            try:
                s.bind(("127.0.0.1", port))
                return port
            except socket.error:
                continue
    return start_port # 如果都没找到，返回初始端口让它报错

if __name__ == "__main__":
    import uvicorn
    # 从环境变量读取端口，默认 8000
    preferred_port = int(os.getenv("APP_PORT", 8000))
    
    # 自动寻找可用端口
    port = find_available_port(preferred_port)
    
    print(f"🚀 后端服务已启动！访问地址: http://127.0.0.1:{port}")
    uvicorn.run(app, host="127.0.0.1", port=port)
