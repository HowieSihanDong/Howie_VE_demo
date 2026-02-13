#!/bin/bash

# 镜像仓库配置
REGISTRY="wangfan-vaps-test-cr-cn-beijing2.cr.volces.com"
NAMESPACE="howie_sql"
IMAGE_NAME="howiesql"
VERSION="v1.0.0"

FULL_IMAGE="${REGISTRY}/${NAMESPACE}/${IMAGE_NAME}:${VERSION}"

echo "======================================"
echo "🐳 Docker 构建脚本"
echo "======================================"
echo ""

# 1. 登录镜像仓库
echo "🔐 步骤 1: 登录镜像仓库..."
docker login --username=sihandong@72042679 ${REGISTRY}
if [ $? -ne 0 ]; then
    echo "❌ 登录失败"
    exit 1
fi
echo "✅ 登录成功"
echo ""

# 2. 构建镜像
echo "🔨 步骤 2: 构建 Docker 镜像..."
docker build -t ${FULL_IMAGE} .
if [ $? -ne 0 ]; then
    echo "❌ 构建失败"
    exit 1
fi
echo "✅ 构建成功: ${FULL_IMAGE}"
echo ""

# 3. 推送镜像
echo "📤 步骤 3: 推送镜像到仓库..."
docker push ${FULL_IMAGE}
if [ $? -ne 0 ]; then
    echo "❌ 推送失败"
    exit 1
fi
echo "✅ 推送成功"
echo ""

echo "======================================"
echo "🎉 完成!"
echo "镜像地址: ${FULL_IMAGE}"
echo "======================================"
