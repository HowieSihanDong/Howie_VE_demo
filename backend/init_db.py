import os
import sqlite3
import random
from datetime import datetime, timedelta

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_FILE = os.path.join(BASE_DIR, "data", "demo.db")

def init_sqlite_db():
    # 1. 连接数据库（如果不存在会自动创建 demo.db 文件）
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    # 2. 创建表
    print("正在创建表结构...")
    cursor.execute("DROP TABLE IF EXISTS ai_projects")
    cursor.execute("""
    CREATE TABLE ai_projects (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        architect_name TEXT NOT NULL,
        project_name TEXT NOT NULL,
        client_industry TEXT,
        tech_stack TEXT,
        episode_count INTEGER,
        total_budget REAL,
        completion_rate INTEGER,
        start_date TEXT,
        end_date TEXT,
        status TEXT,
        ai_tools_used TEXT,
        performance_score REAL
    )
    """)

    # 3. 准备生成 100 条数据
    print("正在生成 100+ 条 AI 短漫剧项目数据...")
    
    industries = ['科幻', '武侠', '悬疑', '都市', '二次元', '治愈', '惊悚']
    statuses = ['已交付', '制作中', '策划中', '后期中']
    tools = ['Stable Diffusion', 'Midjourney', 'Sora', 'Runway', 'Pika', 'Claude 3.5', 'GPT-4o']
    architects = ['张三', '李四', '王五', '赵六', '孙七', '周八', '吴九']

    project_data = []
    
    # 先加几个固定的演示数据
    project_data.append(('张三', '赛博都市：觉醒', '科幻', 'SD + Midjourney', 12, 150000.0, 100, '2023-01-10', '2023-03-10', '已交付', 'Runway Gen-2', 9.5))
    project_data.append(('李四', '古风江湖：剑影', '武侠', 'ControlNet + Sora', 24, 300000.0, 80, '2023-04-15', '2023-08-15', '制作中', 'Pika Labs', 8.8))

    # 循环生成剩下的 100 条
    for i in range(1, 101):
        arch = random.choice(architects)
        proj_name = f"AI短漫剧项目_{i}"
        indus = random.choice(industries)
        tech = " + ".join(random.sample(tools, 2))
        episodes = random.randint(5, 50)
        budget = round(random.uniform(50000, 500000), 2)
        rate = random.randint(0, 100)
        
        start_dt = datetime(2023, 1, 1) + timedelta(days=random.randint(0, 365))
        end_dt = start_dt + timedelta(days=random.randint(30, 180))
        
        status = random.choice(statuses)
        ai_tool = ", ".join(random.sample(tools, 3))
        score = round(random.uniform(5.0, 10.0), 1)
        
        project_data.append((arch, proj_name, indus, tech, episodes, budget, rate, start_dt.strftime('%Y-%m-%d'), end_dt.strftime('%Y-%m-%d'), status, ai_tool, score))

    # 4. 插入数据
    cursor.executemany("""
    INSERT INTO ai_projects (architect_name, project_name, client_industry, tech_stack, episode_count, total_budget, completion_rate, start_date, end_date, status, ai_tools_used, performance_score)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, project_data)

    conn.commit()
    conn.close()
    print(f"✅ 成功！SQLite 数据库已初始化，文件名为: {DB_FILE}")

if __name__ == "__main__":
    init_sqlite_db()
