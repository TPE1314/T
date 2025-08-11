#!/bin/bash

# Telegram Bot 快速启动脚本
# 适用于 Linux 和 macOS 系统

set -e

echo "🚀 Telegram Bot 快速启动脚本"
echo "================================"

# 检查Python版本
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 未安装，正在安装..."
    if command -v apt &> /dev/null; then
        sudo apt update
        sudo apt install -y python3 python3-pip python3-venv
    elif command -v yum &> /dev/null; then
        sudo yum install -y python3 python3-pip
    elif command -v brew &> /dev/null; then
        brew install python3
    else
        echo "❌ 无法自动安装Python3，请手动安装"
        exit 1
    fi
fi

# 检查Python版本
python_version=$(python3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
required_version="3.8"
if [ "$(printf '%s\n' "$required_version" "$python_version" | sort -V | head -n1)" != "$required_version" ]; then
    echo "❌ Python版本过低，需要3.8+，当前版本: $python_version"
    exit 1
fi

echo "✅ Python版本检查通过: $python_version"

# 创建虚拟环境
if [ ! -d "venv" ]; then
    echo "🐍 创建Python虚拟环境..."
    python3 -m venv venv
fi

# 激活虚拟环境
echo "🔧 激活虚拟环境..."
source venv/bin/activate

# 升级pip
echo "📦 升级pip..."
pip install --upgrade pip

# 安装依赖
echo "📦 安装依赖包..."
if [ -f "requirements.txt" ]; then
    pip install -r requirements.txt
else
    echo "❌ requirements.txt 文件不存在"
    exit 1
fi

# 检查配置文件
if [ ! -f ".env" ]; then
    if [ -f "env_example.txt" ]; then
        echo "⚙️ 创建配置文件..."
        cp env_example.txt .env
        echo "⚠️ 请编辑 .env 文件，填入正确的配置信息"
        echo "   特别是 BOT_TOKEN、ADMIN_IDS 和 SUPER_ADMIN_ID"
        read -p "按回车键继续..."
    else
        echo "❌ env_example.txt 文件不存在"
        exit 1
    fi
fi

# 创建必要目录
echo "📁 创建必要目录..."
mkdir -p uploads data updates backups

# 设置权限
chmod +x start_bot.py

# 启动机器人
echo "🤖 启动Telegram Bot..."
echo "💡 使用 Ctrl+C 停止机器人"
echo ""

python3 start_bot.py --mode polling