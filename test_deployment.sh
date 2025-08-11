#!/bin/bash

# 部署测试脚本
# 用于验证部署是否成功

set -e

# 颜色定义
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

# 日志函数
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 测试函数
test_service() {
    local service_name=$1
    local service_display=$2
    
    log_info "测试 $service_display 服务..."
    
    if systemctl is-active --quiet $service_name; then
        log_success "$service_display 服务运行正常"
        return 0
    else
        log_error "$service_display 服务未运行"
        return 1
    fi
}

test_port() {
    local port=$1
    local service_name=$2
    
    log_info "测试端口 $port ($service_name)..."
    
    if netstat -tlnp 2>/dev/null | grep -q ":$port "; then
        log_success "端口 $port 监听正常"
        return 0
    else
        log_error "端口 $port 未监听"
        return 1
    fi
}

test_file() {
    local file_path=$1
    local description=$2
    
    log_info "检查 $description..."
    
    if [ -f "$file_path" ]; then
        log_success "$description 存在"
        return 0
    else
        log_error "$description 不存在: $file_path"
        return 1
    fi
}

test_directory() {
    local dir_path=$1
    local description=$2
    
    log_info "检查 $description..."
    
    if [ -d "$dir_path" ]; then
        log_success "$description 存在"
        return 0
    else
        log_error "$description 不存在: $dir_path"
        return 1
    fi
}

test_command() {
    local command=$1
    local description=$2
    
    log_info "测试 $description..."
    
    if command -v $command &> /dev/null; then
        log_success "$description 可用"
        return 0
    else
        log_error "$description 不可用"
        return 1
    fi
}

# 主测试函数
main() {
    log_info "🚀 开始部署测试..."
    echo ""
    
    local test_results=()
    local total_tests=0
    local passed_tests=0
    
    # 测试系统服务
    log_info "=== 系统服务测试 ==="
    
    total_tests=$((total_tests + 1))
    if test_service "telegram-bot" "Telegram Bot"; then
        passed_tests=$((passed_tests + 1))
        test_results+=("✅ Telegram Bot 服务")
    else
        test_results+=("❌ Telegram Bot 服务")
    fi
    
    total_tests=$((total_tests + 1))
    if test_service "redis-server" "Redis"; then
        passed_tests=$((passed_tests + 1))
        test_results+=("✅ Redis 服务")
    else
        test_results+=("❌ Redis 服务")
    fi
    
    total_tests=$((total_tests + 1))
    if test_service "nginx" "Nginx"; then
        passed_tests=$((passed_tests + 1))
        test_results+=("✅ Nginx 服务")
    else
        test_results+=("❌ Nginx 服务")
    fi
    
    echo ""
    
    # 测试端口监听
    log_info "=== 端口监听测试 ==="
    
    total_tests=$((total_tests + 1))
    if test_port "80" "HTTP"; then
        passed_tests=$((passed_tests + 1))
        test_results+=("✅ HTTP 端口 (80)")
    else
        test_results+=("❌ HTTP 端口 (80)")
    fi
    
    total_tests=$((total_tests + 1))
    if test_port "6379" "Redis"; then
        passed_tests=$((passed_tests + 1))
        test_results+=("✅ Redis 端口 (6379)")
    else
        test_results+=("❌ Redis 端口 (6379)")
    fi
    
    echo ""
    
    # 测试项目文件
    log_info "=== 项目文件测试 ==="
    
    PROJECT_DIR="/home/$(whoami)/telegram-bot"
    
    total_tests=$((total_tests + 1))
    if test_directory "$PROJECT_DIR" "项目目录"; then
        passed_tests=$((passed_tests + 1))
        test_results+=("✅ 项目目录")
    else
        test_results+=("❌ 项目目录")
    fi
    
    total_tests=$((total_tests + 1))
    if test_file "$PROJECT_DIR/bot.py" "主程序文件"; then
        passed_tests=$((passed_tests + 1))
        test_results+=("✅ 主程序文件")
    else
        test_results+=("❌ 主程序文件")
    fi
    
    total_tests=$((total_tests + 1))
    if test_file "$PROJECT_DIR/requirements.txt" "依赖文件"; then
        passed_tests=$((passed_tests + 1))
        test_results+=("✅ 依赖文件")
    else
        test_results+=("❌ 依赖文件")
    fi
    
    total_tests=$((total_tests + 1))
    if test_directory "$PROJECT_DIR/venv" "Python虚拟环境"; then
        passed_tests=$((passed_tests + 1))
        test_results+=("✅ Python虚拟环境")
    else
        test_results+=("❌ Python虚拟环境")
    fi
    
    echo ""
    
    # 测试系统命令
    log_info "=== 系统命令测试 ==="
    
    total_tests=$((total_tests + 1))
    if test_command "python3" "Python3"; then
        passed_tests=$((passed_tests + 1))
        test_results+=("✅ Python3")
    else
        test_results+=("❌ Python3")
    fi
    
    total_tests=$((total_tests + 1))
    if test_command "pip3" "Pip3"; then
        passed_tests=$((passed_tests + 1))
        test_results+=("✅ Pip3")
    else
        test_results+=("❌ Pip3")
    fi
    
    total_tests=$((total_tests + 1))
    if test_command "redis-cli" "Redis CLI"; then
        passed_tests=$((passed_tests + 1))
        test_results+=("✅ Redis CLI")
    else
        test_results+=("❌ Redis CLI")
    fi
    
    echo ""
    
    # 测试网络连接
    log_info "=== 网络连接测试 ==="
    
    total_tests=$((total_tests + 1))
    if curl -f http://localhost/health &> /dev/null; then
        log_success "Nginx 健康检查通过"
        passed_tests=$((passed_tests + 1))
        test_results+=("✅ Nginx 健康检查")
    else
        log_error "Nginx 健康检查失败"
        test_results+=("❌ Nginx 健康检查")
    fi
    
    total_tests=$((total_tests + 1))
    if redis-cli ping &> /dev/null; then
        log_success "Redis 连接测试通过"
        passed_tests=$((passed_tests + 1))
        test_results+=("✅ Redis 连接测试")
    else
        log_error "Redis 连接测试失败"
        test_results+=("❌ Redis 连接测试")
    fi
    
    echo ""
    
    # 显示测试结果
    log_info "=== 测试结果汇总 ==="
    echo ""
    
    for result in "${test_results[@]}"; do
        echo "$result"
    done
    
    echo ""
    echo "📊 测试统计:"
    echo "   总测试数: $total_tests"
    echo "   通过测试: $passed_tests"
    echo "   失败测试: $((total_tests - passed_tests))"
    echo "   成功率: $((passed_tests * 100 / total_tests))%"
    
    echo ""
    
    if [ $passed_tests -eq $total_tests ]; then
        log_success "🎉 所有测试通过！部署成功！"
        echo ""
        echo "📋 下一步操作:"
        echo "1. 配置Bot Token: nano $PROJECT_DIR/.env"
        echo "2. 测试Bot功能"
        echo "3. 配置SSL证书（生产环境）"
        echo "4. 设置监控和备份"
    else
        log_warning "⚠️  部分测试失败，请检查部署日志"
        echo ""
        echo "🔧 故障排除建议:"
        echo "1. 检查服务状态: sudo systemctl status telegram-bot"
        echo "2. 查看系统日志: sudo journalctl -u telegram-bot -f"
        echo "3. 检查配置文件权限"
        echo "4. 确认网络端口未被占用"
    fi
    
    echo ""
    log_info "测试完成！"
}

# 运行主函数
main "$@"