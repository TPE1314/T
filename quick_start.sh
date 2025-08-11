#!/bin/bash

# Telegram Bot 快速启动脚本
# 适用于Linux/macOS系统

set -e

echo "🤖 Telegram Bot 快速启动脚本"
echo "================================"

# 检查Python版本
check_python() {
    if command -v python3 &> /dev/null; then
        PYTHON_CMD="python3"
        PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
    elif command -v python &> /dev/null; then
        PYTHON_CMD="python"
        PYTHON_VERSION=$(python --version 2>&1 | awk '{print $2}')
    else
        echo "❌ 错误: 未找到Python，请先安装Python 3.7+"
        exit 1
    fi
    
    echo "✅ 找到Python: $PYTHON_VERSION"
}

# 检查pip
check_pip() {
    if ! command -v pip3 &> /dev/null && ! command -v pip &> /dev/null; then
        echo "❌ 错误: 未找到pip，请先安装pip"
        exit 1
    fi
    
    if command -v pip3 &> /dev/null; then
        PIP_CMD="pip3"
    else
        PIP_CMD="pip"
    fi
    
    echo "✅ 找到pip: $PIP_CMD"
}

# 安装依赖
install_dependencies() {
    echo "📦 安装Python依赖..."
    $PIP_CMD install -r requirements.txt
    echo "✅ 依赖安装完成"
}

# 配置环境变量
setup_environment() {
    if [ ! -f .env ]; then
        echo "⚙️ 配置环境变量..."
        cp env_example.txt .env
        echo "📝 请编辑 .env 文件，填写正确的BOT_TOKEN"
        echo "💡 提示: 使用 nano .env 或 vim .env 编辑文件"
        read -p "按回车键继续..."
    else
        echo "✅ 环境配置文件已存在"
    fi
}

# 检查配置
check_config() {
    if [ ! -f .env ]; then
        echo "❌ 错误: 未找到 .env 配置文件"
        exit 1
    fi
    
    source .env
    if [ -z "$BOT_TOKEN" ] || [ "$BOT_TOKEN" = "your_bot_token_here" ]; then
        echo "❌ 错误: 请在 .env 文件中设置正确的BOT_TOKEN"
        exit 1
    fi
    
    echo "✅ 配置检查通过"
}

# 创建上传目录
create_upload_dir() {
    mkdir -p uploads
    echo "✅ 上传目录已创建"
}

# 运行测试
run_tests() {
    echo "🧪 运行测试..."
    $PYTHON_CMD test_bot.py
}

# 启动机器人
start_bot() {
    echo "🚀 启动机器人..."
    echo "选择运行模式:"
    echo "1) 轮询模式 (推荐用于开发测试)"
    echo "2) Webhook模式 (推荐用于生产环境)"
    echo "3) 仅检查环境"
    
    read -p "请选择 (1-3): " choice
    
    case $choice in
        1)
            echo "启动轮询模式..."
            $PYTHON_CMD start_bot.py --mode polling
            ;;
        2)
            echo "启动Webhook模式..."
            $PYTHON_CMD start_bot.py --mode webhook
            ;;
        3)
            echo "检查环境配置..."
            $PYTHON_CMD start_bot.py --check-only
            ;;
        *)
            echo "无效选择，启动轮询模式..."
            $PYTHON_CMD start_bot.py --mode polling
            ;;
    esac
}

# 显示帮助信息
show_help() {
    echo "使用方法: $0 [选项]"
    echo ""
    echo "选项:"
    echo "  -h, --help     显示此帮助信息"
    echo "  -t, --test     仅运行测试"
    echo "  -s, --setup    仅进行初始设置"
    echo "  -c, --check    仅检查环境"
    echo ""
    echo "示例:"
    echo "  $0             完整设置和启动"
    echo "  $0 --test     仅运行测试"
    echo "  $0 --setup    仅进行初始设置"
}

# 主函数
main() {
    case "${1:-}" in
        -h|--help)
            show_help
            exit 0
            ;;
        -t|--test)
            check_python
            check_pip
            check_config
            run_tests
            exit 0
            ;;
        -s|--setup)
            check_python
            check_pip
            setup_environment
            create_upload_dir
            echo "✅ 初始设置完成"
            exit 0
            ;;
        -c|--check)
            check_python
            check_pip
            check_config
            echo "✅ 环境检查完成"
            exit 0
            ;;
        "")
            # 默认行为：完整设置和启动
            check_python
            check_pip
            install_dependencies
            setup_environment
            create_upload_dir
            check_config
            run_tests
            start_bot
            ;;
        *)
            echo "❌ 未知选项: $1"
            show_help
            exit 1
            ;;
    esac
}

# 运行主函数
main "$@"