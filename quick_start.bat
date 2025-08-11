@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

echo 🚀 Telegram Bot 快速启动脚本
echo ================================

REM 检查Python版本
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python 未安装，请先安装 Python 3.8+
    echo 下载地址: https://www.python.org/downloads/
    pause
    exit /b 1
)

REM 检查Python版本
for /f "tokens=2" %%i in ('python --version 2^>^&1') do set PYTHON_VERSION=%%i
echo ✅ Python版本检查通过: !PYTHON_VERSION!

REM 创建虚拟环境
if not exist "venv" (
    echo 🐍 创建Python虚拟环境...
    python -m venv venv
)

REM 激活虚拟环境
echo 🔧 激活虚拟环境...
call venv\Scripts\activate.bat

REM 升级pip
echo 📦 升级pip...
python -m pip install --upgrade pip

REM 安装依赖
echo 📦 安装依赖包...
if exist "requirements.txt" (
    pip install -r requirements.txt
) else (
    echo ❌ requirements.txt 文件不存在
    pause
    exit /b 1
)

REM 检查配置文件
if not exist ".env" (
    if exist "env_example.txt" (
        echo ⚙️ 创建配置文件...
        copy env_example.txt .env
        echo ⚠️ 请编辑 .env 文件，填入正确的配置信息
        echo    特别是 BOT_TOKEN、ADMIN_IDS 和 SUPER_ADMIN_ID
        pause
    ) else (
        echo ❌ env_example.txt 文件不存在
        pause
        exit /b 1
    )
)

REM 创建必要目录
echo 📁 创建必要目录...
if not exist "uploads" mkdir uploads
if not exist "data" mkdir data
if not exist "updates" mkdir updates
if not exist "backups" mkdir backups

REM 启动机器人
echo 🤖 启动Telegram Bot...
echo 💡 使用 Ctrl+C 停止机器人
echo.

python start_bot.py --mode polling

pause