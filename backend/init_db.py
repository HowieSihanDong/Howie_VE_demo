import os
import mysql.connector
import random
from datetime import datetime, timedelta
from dotenv import load_dotenv

# 加载环境变量
env_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'config', '.env')
load_dotenv(env_path)

# MySQL 数据库配置
DB_CONFIG = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'port': int(os.getenv('DB_PORT', 3306)),
    'user': os.getenv('DB_USER', 'root'),
    'password': os.getenv('DB_PASSWORD', ''),
    'charset': 'utf8mb4'
}

DB_NAME = os.getenv('DB_NAME', 'demo_db')

def init_mysql_db():
    # 1. 先连接 MySQL（不指定数据库）
    conn = mysql.connector.connect(**DB_CONFIG)
    cursor = conn.cursor()
    
    # 2. 创建数据库
    print(f"正在创建数据库 {DB_NAME}...")
    cursor.execute(f"CREATE DATABASE IF NOT EXISTS {DB_NAME} CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
    cursor.execute(f"USE {DB_NAME}")
    
    # 3. 创建表
    print("正在创建表结构...")
    cursor.execute("DROP TABLE IF EXISTS ai_projects")
    cursor.execute("""
    CREATE TABLE ai_projects (
        id INT AUTO_INCREMENT PRIMARY KEY,
        architect_name VARCHAR(100) NOT NULL COMMENT '解决方案架构师姓名',
        project_name VARCHAR(200) NOT NULL COMMENT 'AI短漫剧项目名称',
        client_industry VARCHAR(100) COMMENT '客户行业',
        tech_stack VARCHAR(255) COMMENT '技术栈',
        episode_count INT COMMENT '剧集数量',
        total_budget DECIMAL(15, 2) COMMENT '项目总预算',
        completion_rate INT COMMENT '完成进度(%)',
        start_date DATE COMMENT '开始日期',
        end_date DATE COMMENT '交付日期',
        status VARCHAR(50) COMMENT '当前状态',
        ai_tools_used VARCHAR(255) COMMENT '使用的AI工具',
        performance_score DECIMAL(3, 1) COMMENT '性能/评价得分'
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
    """)

    # 4. 准备生成 100 条数据
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

    # 5. 插入数据
    cursor.executemany("""
    INSERT INTO ai_projects (architect_name, project_name, client_industry, tech_stack, episode_count, total_budget, completion_rate, start_date, end_date, status, ai_tools_used, performance_score)
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """, project_data)

    conn.commit()
    cursor.close()
    conn.close()
    print(f"✅ 成功！MySQL 数据库已初始化，数据库: {DB_NAME}")

if __name__ == "__main__":
    init_mysql_db()
