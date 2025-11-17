@echo off
chcp 65001 >nul
echo ========================================
echo    手机监控服务端启动脚本
echo ========================================
echo.

REM 检查Python是否安装
python --version >nul 2>&1
if errorlevel 1 (
    echo [错误] 未检测到Python，请先安装Python 3.6+
    pause
    exit /b 1
)

echo [信息] 正在启动服务端...
echo.

REM 启动服务端
python server.py

pause
