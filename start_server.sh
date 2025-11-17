#!/bin/bash

echo "========================================"
echo "   手机监控服务端启动脚本"
echo "========================================"
echo ""

# 检查Python是否安装
if ! command -v python3 &> /dev/null; then
    echo "[错误] 未检测到Python3，请先安装"
    exit 1
fi

echo "[信息] 正在启动服务端..."
echo ""

# 启动服务端
python3 server.py
