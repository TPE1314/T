@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

echo 🤖 Telegram Bot 快速启动脚本 (Windows)
echo ================================

:: 检查Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ 错误: 未找到Python，请先安装Python 3.7+
    pause
    exit /b 1
)

echo ✅ 找到Python

:: 检查pip
pip --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ 错误: 未找到pip，请先安装pip
    pause
    exit /b 1
)

echo ✅ 找到pip

:: 安装依赖
echo 📦 安装Python依赖...
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo ❌ 依赖安装失败
    pause
    exit /b 1
)
echo ✅ 依赖安装完成

:: 配置环境变量
if not exist .env (
    echo ⚙️ 配置环境变量...
    copy env_example.txt .env >nul
    echo 📝 请编辑 .env 文件，填写正确的BOT_TOKEN
    echo 💡 提示: 使用记事本或其他文本编辑器编辑 .env 文件
    pause
) else (
    echo ✅ 环境配置文件已存在
)

:: 创建上传目录
if not exist uploads mkdir uploads
echo ✅ 上传目录已创建

:: 检查配置
if not exist .env (
    echo ❌ 错误: 未找到 .env 配置文件
    pause
    exit /b 1
)

:: 运行测试
echo 🧪 运行测试...
python test_bot.py
if %errorlevel% neq 0 (
    echo ❌ 测试失败
    pause
    exit /b 1
)

:: 启动机器人
echo 🚀 启动机器人...
echo 选择运行模式:
echo 1) 轮询模式 (推荐用于开发测试)
echo 2) Webhook模式 (推荐用于生产环境)
echo 3) 仅检查环境

set /p choice="请选择 (1-3): "

if "%choice%"=="1" (
    echo 启动轮询模式...
    python start_bot.py --mode polling
) else if "%choice%"=="2" (
    echo 启动Webhook模式...
    python start_bot.py --mode webhook
) else if "%choice%"=="3" (
    echo 检查环境配置...
    python start_bot.py --check-only
) else (
    echo 无效选择，启动轮询模式...
    python start_bot.py --mode polling
)

pause