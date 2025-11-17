@echo off
chcp 65001 >nul
echo ========================================
echo    手机监控客户端启动脚本
echo ========================================
echo.

REM 检查Python是否安装
python --version >nul 2>&1
if errorlevel 1 (
    echo [错误] 未检测到Python，请先安装Python 3.6+
    pause
    exit /b 1
)

echo 请输入服务器IP地址（例如：192.168.1.100）
set /p SERVER_IP=IP地址: 

if "%SERVER_IP%"=="" (
    echo [错误] IP地址不能为空
    pause
    exit /b 1
)

echo.
echo [信息] 正在连接到 %SERVER_IP%:8888 ...
echo.

REM 启动客户端
python client.py %SERVER_IP%

pause
