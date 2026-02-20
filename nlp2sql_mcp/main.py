from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import os
from dotenv import load_dotenv

# 引入你的LLM服务（已验证可用）
from llm_service import get_sql_from_llm

# ========== 基础配置 ==========
# 加载环境变量（适配函数服务，优先读取函数的环境变量）
if os.getenv("VEFAAS_ENV") is None:  # VEFAAS_ENV 是函数服务的内置环境变量
    load_dotenv()
else:
    print("📌 运行在函数服务环境，跳过 .env 文件加载")
# 初始化FastAPI（自动生成OpenAPI 3.0文档，适配MCP要求）
app = FastAPI(
    title="nlp2sql-mcp-service",  # MCP要求的必填title
    version="1.0.0",              # MCP要求的必填version
    description="仅返回SQL代码的NLP2SQL MCP服务"
)

# ========== 数据模型（适配MCP的请求/响应规范） ==========
# 请求体：接收用户的自然语言查询
class NLP2SQLRequest(BaseModel):
    prompt: str  # 用户输入的自然语言，比如"查询2024年10月的订单数"

# 响应体：仅返回生成的SQL代码（MCP核心需求）
class NLP2SQLResponse(BaseModel):
    status: str  # success/error
    sql: str     # 生成的SQL代码
    message: str = ""  # 错误信息（可选）

# ========== 核心接口（适配MCP） ==========
@app.post(
    "/generate-sql",  # 简洁的接口路径
    operation_id="generate_sql",  # MCP要求的operationId
    response_model=NLP2SQLResponse
)
async def generate_sql(request: NLP2SQLRequest):
    """
    核心接口：接收自然语言，返回生成的SQL代码（仅生成，不执行）
    """
    # 校验输入
    if not request.prompt.strip():
        raise HTTPException(status_code=400, detail="输入的自然语言查询不能为空")
    
    try:
        # 调用你的LLM服务生成SQL（核心逻辑，保留不变）
        prompt = request.prompt.strip()
        sql = get_sql_from_llm(prompt)
        
        # 仅返回SQL，去掉数据库执行、缓存等逻辑
        return NLP2SQLResponse(
            status="success",
            sql=sql
        )
    except Exception as e:
        # 异常处理，返回错误信息
        raise HTTPException(
            status_code=500,
            detail=f"生成SQL失败：{str(e)}"
        )

# ========== 函数服务启动配置 ==========
# 适配火山引擎函数服务的启动逻辑（监听0.0.0.0，端口固定8000）
if __name__ == "__main__":
    import uvicorn
    # 函数服务中必须监听0.0.0.0，端口固定为8000（和函数配置一致）
    uvicorn.run(app, host="0.0.0.0", port=8000)