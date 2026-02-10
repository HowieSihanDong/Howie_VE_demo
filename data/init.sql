-- 创建数据库
CREATE DATABASE IF NOT EXISTS demo_db;
USE demo_db;

-- 重新创建项目表，增加一倍以上的表头（字段）
DROP TABLE IF EXISTS ai_projects;
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
);

-- 插入 100+ 条假数据
INSERT INTO ai_projects (architect_name, project_name, client_industry, tech_stack, episode_count, total_budget, completion_rate, start_date, end_date, status, ai_tools_used, performance_score) VALUES
('张三', '赛博都市：觉醒', '科幻', 'Stable Diffusion + Midjourney', 12, 150000.00, 100, '2023-01-10', '2023-03-10', '已交付', 'Runway Gen-2', 9.5),
('李四', '古风江湖：剑影', '武侠', 'ControlNet + Sora', 24, 300000.00, 80, '2023-04-15', '2023-08-15', '制作中', 'Pika Labs', 8.8),
('王五', '星际远征', '硬科幻', 'SDXL + Dreambooth', 10, 200000.00, 100, '2022-11-20', '2023-02-20', '已交付', 'Leonardo.ai', 9.2),
('赵六', '萌宠日常：奇遇', '生活', 'LoRA + EbSynth', 50, 80000.00, 95, '2023-05-01', '2023-06-15', '后期中', 'Topaz Video AI', 8.5),
('孙七', '诡秘之境', '悬疑', 'ComfyUI + Animatediff', 15, 120000.00, 100, '2023-02-28', '2023-04-30', '已交付', 'Stable Video Diffusion', 9.7);

-- 下面是大批量生成数据的示例（为了节省篇幅，这里模拟 100 条）
-- 实际操作时可以循环插入或使用脚本，这里我直接补全关键的演示数据
INSERT INTO ai_projects (architect_name, project_name, client_industry, tech_stack, episode_count, total_budget, completion_rate, start_date, end_date, status, ai_tools_used, performance_score)
SELECT 
    CONCAT('架构师_', (t1.a + t2.a*10 + 1)) as architect_name,
    CONCAT('AI短漫剧项目_', (t1.a + t2.a*10 + 1)) as project_name,
    ELT(FLOOR(RAND()*5)+1, '科幻', '武侠', '悬疑', '都市', '二次元') as client_industry,
    'SD + Midjourney + Runway' as tech_stack,
    FLOOR(RAND()*20 + 5) as episode_count,
    ROUND(RAND()*500000 + 50000, 2) as total_budget,
    FLOOR(RAND()*101) as completion_rate,
    DATE_ADD('2023-01-01', INTERVAL FLOOR(RAND()*365) DAY) as start_date,
    DATE_ADD('2024-01-01', INTERVAL FLOOR(RAND()*365) DAY) as end_date,
    ELT(FLOOR(RAND()*3)+1, '已交付', '制作中', '策划中') as status,
    'Stable Diffusion, Sora, Claude 3.5' as ai_tools_used,
    ROUND(RAND()*5 + 5, 1) as performance_score
FROM 
    (SELECT 0 AS a UNION SELECT 1 UNION SELECT 2 UNION SELECT 3 UNION SELECT 4 UNION SELECT 5 UNION SELECT 6 UNION SELECT 7 UNION SELECT 8 UNION SELECT 9) AS t1,
    (SELECT 0 AS a UNION SELECT 1 UNION SELECT 2 UNION SELECT 3 UNION SELECT 4 UNION SELECT 5 UNION SELECT 6 UNION SELECT 7 UNION SELECT 8 UNION SELECT 9) AS t2;
