import os
import sys

# 将 backend 目录添加到 sys.path，以便导入 llm_service
BASE_DIR = os.path.dirname(os.path.dirname(__file__))
sys.path.append(os.path.join(BASE_DIR, 'backend'))

from llm_service import get_sql_from_llm

def test_llm_connection():
    print("🔍 --- 正在开始 AI 连通性测试 ---")
    
    # 1. 检查 API Key
    api_key = os.getenv("ARK_API_KEY")
    if not api_key or "你的" in api_key:
        print("❌ 错误：未检测到有效的 ARK_API_KEY！")
        print("请检查 .env 文件，确保 ARK_API_KEY 已经填入正确的密钥。")
        return

    # 2. 测试简单查询
    test_prompt = "查询所有架构师的名字"
    print(f"📡 正在发送测试问题: '{test_prompt}'")
    
    try:
        # 调用 AI 获取 SQL
        sql = get_sql_from_llm(test_prompt)
        
        print("\n--- SQL 变量结构分析 ---")
        print(f"数据类型 (Type): {type(sql)}")
        print(f"变量内容 (Value): {sql}")
        print("------------------------\n")
        
        # 3. 验证结果
        if isinstance(sql, str) and "SELECT" in sql.upper():
            print(f"✅ AI 调用成功！")
        else:
            print(f"⚠️ AI 返回的结果不符合预期，请检查 llm_service.py 中的解析逻辑。")
            
    except Exception as e:
        print(f"❌ 测试过程中发生异常: {e}")

if __name__ == "__main__":
    test_llm_connection()
