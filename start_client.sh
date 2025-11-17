#!/bin/bash

echo "========================================"
echo "   手机监控客户端启动脚本"
echo "========================================"
echo ""

# 检查Python是否安装
if ! command -v python3 &> /dev/null; then
    echo "[错误] 未检测到Python3，请先安装"
    exit 1
fi

echo "请输入服务器IP地址（例如：192.168.1.100）"
read -p "IP地址: " SERVER_IP

if [ -z "$SERVER_IP" ]; then
    echo "[错误] IP地址不能为空"
    exit 1
fi

echo ""
echo "[信息] 正在连接到 $SERVER_IP:8888 ..."
echo ""

# 启动客户端
python3 client.py $SERVER_IP
