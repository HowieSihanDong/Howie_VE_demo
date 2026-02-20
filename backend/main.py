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

# 加载环境变量（从 config/.env 读取）
env_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'config', '.env')
load_dotenv(env_path)

app = FastAPI()

# 1. 允许跨域请求
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# 2. MySQL 数据库配置（读取火山引擎 RDS 配置）
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

# 3. 初始化 Redis 连接（适配火山引擎私网 Redis）
redis_client = None
try:
    # 从 .env 读取 Redis 配置
    redis_host = os.getenv('REDIS_HOST', 'localhost')
    redis_port = int(os.getenv('REDIS_PORT', 6379))
    redis_user = os.getenv('REDIS_USER', 'default')  # 新增这行
    redis_password = os.getenv('REDIS_PASSWORD', '')
    redis_db = int(os.getenv('REDIS_DB', 0))
    
    # 创建 Redis 客户端（适配火山引擎私网）
    redis_client = redis.Redis(
        host=redis_host,
        port=redis_port,
        username=redis_user,  # 新增这行
        password=redis_password,
        db=redis_db,
        decode_responses=True,  # 自动解码为字符串
        socket_timeout=10,      # 私网连接超时设为10秒
        retry_on_timeout=True   # 超时自动重试
    )
    
    # 测试连接
    redis_client.ping()
    print(f"✅ Redis 私网连接成功: {redis_host}:{redis_port}/db{redis_db}")
except redis.exceptions.AuthenticationError:
    print(f"⚠️ Redis 认证失败: 密码错误，请检查 REDIS_PASSWORD 配置")
except redis.exceptions.ConnectionError:
    print(f"⚠️ Redis 连接失败: 无法连接到 {redis_host}:{redis_port}")
    print("   请检查：1.Redis白名单是否包含ECS IP  2.ECS和Redis是否在同一VPC  3.端口是否开放")
except Exception as e:
    print(f"⚠️ Redis 初始化异常: {str(e)}，将使用内存 Mock 缓存")

# 内存 Mock 缓存（备用）
mock_cache = {}

# 请求模型定义
class QueryRequest(BaseModel):
    prompt: str

def get_db_connection():
    """获取 MySQL 数据库连接"""
    return mysql.connector.connect(**DB_CONFIG)

@app.post("/ask")
async def ask_ai_and_query(request: QueryRequest):
    """处理前端请求的主接口，支持 Redis 缓存"""
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
        except Exception as e:
            print(f"⚠️ Redis 缓存读取失败: {e}")
    elif prompt in mock_cache:
        sql = mock_cache[prompt]
        cache_hit = True
        print(f"📦 [Mock 缓存命中] 从内存读取 SQL")

    # --- 未命中缓存则调用 AI 生成 SQL ---
    if not sql:
        print("🤖 [AI 调用] 正在生成 SQL...")
        sql = get_sql_from_llm(prompt)
        
        # 存入缓存（有效期 1 小时）
        if redis_client:
            try:
                redis_client.setex(f"cache:{prompt}", 3600, sql)
                print(f"💾 [Redis 缓存] 已存入: cache:{prompt}")
            except Exception as e:
                print(f"⚠️ Redis 缓存写入失败: {e}")
        else:
            mock_cache[prompt] = sql

    print(f"[最终 SQL] {sql}")
    
    # --- 执行 SQL 查询 MySQL ---
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
            "cache_hit": cache_hit
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

# 托管前端静态文件
app.mount("/", StaticFiles(directory=FRONTEND_DIR, html=True), name="frontend")

@app.get("/")
async def read_index():
    return FileResponse(os.path.join(FRONTEND_DIR, 'index.html'))

# 自动查找可用端口
import socket
def find_available_port(start_port: int, max_attempts: int = 10):
    for port in range(start_port, start_port + max_attempts):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            try:
                s.bind(("0.0.0.0", port))
                return port
            except socket.error:
                continue
    return start_port

if __name__ == "__main__":
    import uvicorn
    # 从环境变量读取端口，默认 8000
    preferred_port = int(os.getenv("APP_PORT", 8000))
    port = find_available_port(preferred_port)
    
    print(f"🚀 后端服务已启动！访问地址: http://0.0.0.0:{port}")
    # 改为 0.0.0.0 允许外网访问（ECS 上需要）
    uvicorn.run(app, host="0.0.0.0", port=port)