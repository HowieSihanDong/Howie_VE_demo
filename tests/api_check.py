import os
import sys
from volcenginesdkarkruntime import Ark
from dotenv import load_dotenv

# 1. 加载 .env 文件中的环境变量
BASE_DIR = os.path.dirname(os.path.dirname(__file__))
env_path = os.path.join(BASE_DIR, 'config', '.env')
load_dotenv(env_path)

# 2. 从环境变量中获取 API KEY
api_key = os.getenv('ARK_API_KEY')

# 安全打印函数（解决中文编码问题）
def safe_print(content):
    """
    安全打印函数，绕过系统默认编码限制
    """
    try:
        # 尝试正常打印
        print(content)
    except UnicodeEncodeError:
        # 如果编码失败，使用字节流输出
        if isinstance(content, str):
            sys.stdout.buffer.write(content.encode('utf-8') + b'\n')
        else:
            sys.stdout.buffer.write(str(content).encode('utf-8') + b'\n')

# 打印 API Key（使用安全打印）
if api_key:
    safe_print(f"✅ 已成功读取 API Key: {api_key[:6]}******")
else:
    safe_print("❌ 错误：未在 .env 文件中找到 ARK_API_KEY！请检查文件内容。")

# 3. 初始化 Ark 客户端
client = Ark(
    base_url="https://ark.cn-beijing.volces.com/api/v3",
    api_key=api_key,
)

safe_print("正在发起 API 请求，请稍候...")

try:
    # 4. 调用火山引擎 API
    response = client.responses.create(
        model="doubao-seed-1-8-251228",
        input=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "input_image",
                        "image_url": "https://ark-project.tos-cn-beijing.volces.com/doc_image/ark_demo_img_1.png"
                    },
                    {
                        "type": "input_text",
                        "text": "你看见了什么？"
                    },
                ],
            }
        ]
    )

    # 5. 解析响应结果
    safe_print("\n--- AI 响应结果 ---")
    response_dict = {}
    if hasattr(response, 'to_dict'):
        response_dict = response.to_dict()
    elif hasattr(response, '__dict__'):
        response_dict = vars(response)
    
    # 方式1：写入文件（最稳妥，避免终端编码问题）
    log_path = os.path.join(BASE_DIR, 'logs', 'ai_response.txt')
    with open(log_path, 'w', encoding='utf-8') as f:
        import json
        json.dump(response_dict, f, ensure_ascii=False, indent=2)
    safe_print(f"✅ 响应结果已保存到 {log_path} 文件（UTF-8 编码）")
    
    # 方式2：安全打印核心内容
    if response_dict:
        # 提取核心回答
        try:
            choices = response_dict.get('output', {}).get('choices', [])
            if choices:
                content = choices[0].get('message', {}).get('content', '')
                safe_print(f"📝 AI 回答：{content}")
            else:
                safe_print(f"📊 响应状态：{response_dict.get('status', '未知')}")
        except Exception as e:
            safe_print(f"⚠️  解析内容失败：{e}")
            safe_print(f"📋 完整响应：{str(response_dict)[:500]}...")

except Exception as e:
    safe_print(f"\n❌ 请求失败了：{e}")
    # 保存错误信息到文件
    err_log_path = os.path.join(BASE_DIR, 'logs', 'error_log.txt')
    with open(err_log_path, 'w', encoding='utf-8') as f:
        f.write(f"错误类型：{type(e).__name__}\n")
        f.write(f"错误信息：{str(e)}\n")
        import traceback
        f.write(f"详细堆栈：{traceback.format_exc()}\n")
    safe_print(f"❌ 错误详情已保存到 {err_log_path} 文件")