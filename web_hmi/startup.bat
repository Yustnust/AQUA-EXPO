@echo off
REM AQUA-EXPO Web HMI 开机自启动脚本
REM 将此脚本的快捷方式放入 Windows 启动文件夹：
REM   Win+R → shell:startup → 创建快捷方式

cd /d "%~dp0backend"

REM 创建必要目录
if not exist "data" mkdir data
if not exist "logs" mkdir logs

REM 启动后端服务（日志输出到文件）
start /min "AQUA-EXPO-HMI" cmd /c "uvicorn app.main:app --host 0.0.0.0 --port 8000 > ..\logs\backend.log 2>&1"

REM 等待后端启动
timeout /t 5 /nobreak >nul

REM 在默认浏览器中打开 HMI
start http://localhost:8000