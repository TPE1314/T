#!/bin/bash

# Telegram Bot Docker 部署脚本
# 适用于 Linux 和 macOS 系统

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

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

# 检查Docker是否安装
check_docker() {
    if ! command -v docker &> /dev/null; then
        log_error "Docker 未安装，请先安装 Docker"
        exit 1
    fi
    
    if ! command -v docker-compose &> /dev/null; then
        log_error "Docker Compose 未安装，请先安装 Docker Compose"
        exit 1
    fi
    
    log_success "Docker 环境检查通过"
}

# 检查配置文件
check_config() {
    if [ ! -f ".env" ]; then
        if [ -f "env_example.txt" ]; then
            log_warning "未找到 .env 配置文件，正在创建..."
            cp env_example.txt .env
            log_warning "请编辑 .env 文件，填入正确的配置信息"
            log_warning "特别是 BOT_TOKEN、ADMIN_IDS 和 SUPER_ADMIN_ID"
            read -p "按回车键继续..."
        else
            log_error "未找到配置文件模板 env_example.txt"
            exit 1
        fi
    fi
    
    # 检查必要的配置
    source .env
    if [ -z "$BOT_TOKEN" ] || [ "$BOT_TOKEN" = "your_bot_token_here" ]; then
        log_error "请在 .env 文件中设置正确的 BOT_TOKEN"
        exit 1
    fi
    
    if [ -z "$ADMIN_IDS" ]; then
        log_error "请在 .env 文件中设置 ADMIN_IDS"
        exit 1
    fi
    
    if [ -z "$SUPER_ADMIN_ID" ]; then
        log_error "请在 .env 文件中设置 SUPER_ADMIN_ID"
        exit 1
    fi
    
    log_success "配置文件检查通过"
}

# 创建必要的目录
create_directories() {
    log_info "创建必要的目录..."
    mkdir -p uploads data updates backups logs ssl monitoring
    
    # 设置权限
    chmod 755 uploads data updates backups logs ssl monitoring
    
    log_success "目录创建完成"
}

# 生成自签名SSL证书（用于测试）
generate_ssl_cert() {
    if [ ! -f "ssl/cert.pem" ] || [ ! -f "ssl/key.pem" ]; then
        log_info "生成自签名SSL证书..."
        mkdir -p ssl
        
        # 生成私钥
        openssl genrsa -out ssl/key.pem 2048
        
        # 生成证书
        openssl req -new -x509 -key ssl/key.pem -out ssl/cert.pem -days 365 -subj "/C=CN/ST=State/L=City/O=Organization/CN=localhost"
        
        log_success "SSL证书生成完成"
    else
        log_info "SSL证书已存在"
    fi
}

# 构建Docker镜像
build_images() {
    log_info "构建Docker镜像..."
    docker-compose build --no-cache
    
    if [ $? -eq 0 ]; then
        log_success "Docker镜像构建完成"
    else
        log_error "Docker镜像构建失败"
        exit 1
    fi
}

# 启动服务
start_services() {
    log_info "启动服务..."
    docker-compose up -d
    
    if [ $? -eq 0 ]; then
        log_success "服务启动完成"
    else
        log_error "服务启动失败"
        exit 1
    fi
}

# 检查服务状态
check_services() {
    log_info "检查服务状态..."
    sleep 10  # 等待服务启动
    
    # 检查容器状态
    docker-compose ps
    
    # 检查健康状态
    log_info "检查服务健康状态..."
    
    # 检查Telegram Bot
    if curl -f http://localhost:8443/health &> /dev/null; then
        log_success "Telegram Bot 服务正常"
    else
        log_warning "Telegram Bot 服务可能未完全启动"
    fi
    
    # 检查Redis
    if docker exec bot-redis redis-cli ping &> /dev/null; then
        log_success "Redis 服务正常"
    else
        log_warning "Redis 服务可能未完全启动"
    fi
    
    # 检查Nginx
    if curl -f http://localhost/health &> /dev/null; then
        log_success "Nginx 服务正常"
    else
        log_warning "Nginx 服务可能未完全启动"
    fi
}

# 显示服务信息
show_service_info() {
    log_info "服务部署完成！"
    echo ""
    echo "🌐 服务访问地址："
    echo "   - HTTP:  http://localhost"
    echo "   - HTTPS: https://localhost"
    echo "   - Bot API: http://localhost:8443"
    echo "   - Redis:  localhost:6379"
    echo "   - 监控:   http://localhost:9090"
    echo ""
    echo "📁 数据目录："
    echo "   - 上传文件: ./uploads"
    echo "   - 数据库:   ./data"
    echo "   - 更新文件: ./updates"
    echo "   - 备份文件: ./backups"
    echo "   - 日志文件: ./logs"
    echo ""
    echo "🔧 常用命令："
    echo "   - 查看状态: docker-compose ps"
    echo "   - 查看日志: docker-compose logs -f"
    echo "   - 停止服务: docker-compose down"
    echo "   - 重启服务: docker-compose restart"
    echo "   - 更新服务: docker-compose pull && docker-compose up -d"
    echo ""
    echo "⚠️  注意："
    echo "   - 首次使用请确保 .env 配置正确"
    echo "   - 生产环境请使用正式的SSL证书"
    echo "   - 定期备份 data 目录"
}

# 停止服务
stop_services() {
    log_info "停止服务..."
    docker-compose down
    log_success "服务已停止"
}

# 清理资源
cleanup() {
    log_info "清理Docker资源..."
    docker-compose down -v --remove-orphans
    docker system prune -f
    log_success "清理完成"
}

# 显示帮助信息
show_help() {
    echo "使用方法: $0 [选项]"
    echo ""
    echo "选项:"
    echo "  start     启动服务（默认）"
    echo "  stop      停止服务"
    echo "  restart   重启服务"
    echo "  status    查看服务状态"
    echo "  logs      查看服务日志"
    echo "  build     重新构建镜像"
    echo "  cleanup   清理资源"
    echo "  help      显示此帮助信息"
    echo ""
    echo "示例:"
    echo "  $0             启动服务"
    echo "  $0 start       启动服务"
    echo "  $0 stop        停止服务"
    echo "  $0 restart     重启服务"
    echo "  $0 status      查看状态"
    echo "  $0 logs        查看日志"
    echo "  $0 build       重新构建"
    echo "  $0 cleanup     清理资源"
}

# 主函数
main() {
    case "${1:-start}" in
        start)
            log_info "🚀 开始部署 Telegram Bot..."
            check_docker
            check_config
            create_directories
            generate_ssl_cert
            build_images
            start_services
            check_services
            show_service_info
            ;;
        stop)
            stop_services
            ;;
        restart)
            log_info "🔄 重启服务..."
            stop_services
            sleep 2
            start_services
            check_services
            ;;
        status)
            docker-compose ps
            ;;
        logs)
            docker-compose logs -f
            ;;
        build)
            check_docker
            check_config
            build_images
            ;;
        cleanup)
            cleanup
            ;;
        help|--help|-h)
            show_help
            ;;
        *)
            log_error "未知选项: $1"
            show_help
            exit 1
            ;;
    esac
}

# 运行主函数
main "$@"