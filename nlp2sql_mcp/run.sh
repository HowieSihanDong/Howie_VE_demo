#!/bin/bash
# 安装依赖（使用清华源加速）
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
# 启动服务（固定端口8000，和函数配置一致）
uvicorn main:app --host 0.0.0.0 --port 8000