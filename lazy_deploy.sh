#!/bin/bash

# 🚀 Telegram Bot 懒人版一键部署脚本
# 支持Ubuntu/CentOS/Debian等Linux系统
# 自动检测系统类型并完成部署

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

# 项目配置
PROJECT_NAME="telegram-bot"
PROJECT_VERSION="2.1.0"

# 检测系统类型
detect_system() {
    log_info "🔍 检测系统环境..."
    
    if [ -f /etc/os-release ]; then
        . /etc/os-release
        OS_NAME=$NAME
        OS_VERSION=$VERSION_ID
        OS_ID=$ID
    elif [ -f /etc/redhat-release ]; then
        OS_NAME=$(cat /etc/redhat-release)
        OS_ID="rhel"
    else
        log_error "无法检测系统类型"
        exit 1
    fi
    
    log_success "检测到系统: $OS_NAME $OS_VERSION"
    
    # 设置包管理器
    case $OS_ID in
        ubuntu|debian)
            PKG_MANAGER="apt"
            PKG_UPDATE="apt update"
            PKG_INSTALL="apt install -y"
            ;;
        centos|rhel|fedora)
            PKG_MANAGER="yum"
            PKG_UPDATE="yum update -y"
            PKG_INSTALL="yum install -y"
            ;;
        *)
            log_error "不支持的系统类型: $OS_ID"
            exit 1
            ;;
    esac
    
    log_info "使用包管理器: $PKG_MANAGER"
}

# 检查用户权限
check_permissions() {
    log_info "🔐 检查用户权限..."
    
    if [ "$EUID" -eq 0 ]; then
        log_warning "检测到root用户，将使用root权限进行部署"
        log_info "注意：生产环境建议使用普通用户+sudo权限"
        read -p "是否继续？(y/N): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            log_info "部署已取消"
            exit 0
        fi
        USER_NAME="root"
        PROJECT_DIR="/root/$PROJECT_NAME"
        SUDO_CMD=""
    else
        if command -v sudo &> /dev/null; then
            log_success "检测到普通用户，将使用sudo权限"
            USER_NAME=$(whoami)
            PROJECT_DIR="/home/$USER_NAME/$PROJECT_NAME"
            SUDO_CMD="sudo"
        else
            log_error "未安装sudo，请先安装sudo或使用root用户"
            exit 1
        fi
    fi
    
    log_info "用户: $USER_NAME"
    log_info "项目目录: $PROJECT_DIR"
}

# 更新系统
update_system() {
    log_info "📦 更新系统包..."
    
    if [ "$PKG_MANAGER" = "apt" ]; then
        $SUDO_CMD apt update
        $SUDO_CMD apt upgrade -y
    elif [ "$PKG_MANAGER" = "yum" ]; then
        $SUDO_CMD yum update -y
    fi
    
    log_success "系统更新完成"
}

# 安装基础依赖
install_basic_deps() {
    log_info "🔧 安装基础依赖..."
    
    if [ "$PKG_MANAGER" = "apt" ]; then
        $SUDO_CMD apt install -y \
            python3 \
            python3-pip \
            python3-venv \
            python3-dev \
            curl \
            wget \
            git \
            build-essential \
            ufw \
            supervisor \
            logrotate \
            cron \
            rsyslog
    elif [ "$PKG_MANAGER" = "yum" ]; then
        $SUDO_CMD yum install -y \
            python3 \
            python3-pip \
            python3-devel \
            curl \
            wget \
            git \
            gcc \
            gcc-c++ \
            make \
            firewalld \
            supervisor \
            logrotate \
            cronie \
            rsyslog
    fi
    
    log_success "基础依赖安装完成"
}

# 安装Redis
install_redis() {
    log_info "🔴 安装Redis..."
    
    if [ "$PKG_MANAGER" = "apt" ]; then
        $SUDO_CMD apt install -y redis-server
        $SUDO_CMD systemctl enable redis-server
        $SUDO_CMD systemctl start redis-server
    elif [ "$PKG_MANAGER" = "yum" ]; then
        $SUDO_CMD yum install -y redis
        $SUDO_CMD systemctl enable redis
        $SUDO_CMD systemctl start redis
    fi
    
    log_success "Redis安装完成"
}

# 安装Nginx
install_nginx() {
    log_info "🌐 安装Nginx..."
    
    if [ "$PKG_MANAGER" = "apt" ]; then
        $SUDO_CMD apt install -y nginx
        $SUDO_CMD systemctl enable nginx
        $SUDO_CMD systemctl start nginx
    elif [ "$PKG_MANAGER" = "yum" ]; then
        $SUDO_CMD yum install -y nginx
        $SUDO_CMD systemctl enable nginx
        $SUDO_CMD systemctl start nginx
    fi
    
    log_success "Nginx安装完成"
}

# 创建项目目录
create_project_dirs() {
    log_info "📁 创建项目目录..."
    
    $SUDO_CMD mkdir -p $PROJECT_DIR/{app,static,uploads,data,logs,backups,config,ssl}
    $SUDO_CMD chown -R $USER_NAME:$USER_NAME $PROJECT_DIR
    
    log_success "项目目录创建完成"
}

# 复制项目文件
copy_project_files() {
    log_info "📋 复制项目文件..."
    
    # 获取当前脚本所在目录
    SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
    
    # 复制项目文件
    $SUDO_CMD cp -r $SCRIPT_DIR/* $PROJECT_DIR/
    $SUDO_CMD chown -R $USER_NAME:$USER_NAME $PROJECT_DIR
    
    log_success "项目文件复制完成"
}

# 创建Python环境
create_python_env() {
    log_info "🐍 创建Python虚拟环境..."
    
    cd $PROJECT_DIR
    
    # 创建虚拟环境
    python3 -m venv venv
    source venv/bin/activate
    
    # 升级pip
    pip install --upgrade pip
    
    # 安装依赖
    if [ -f requirements.txt ]; then
        pip install -r requirements.txt
    else
        log_warning "未找到requirements.txt，跳过依赖安装"
    fi
    
    log_success "Python环境创建完成"
}

# 创建启动脚本
create_startup_script() {
    log_info "🚀 创建启动脚本..."
    
    cat > $PROJECT_DIR/start_bot.sh << EOF
#!/bin/bash
cd $PROJECT_DIR
source venv/bin/activate
python bot.py
EOF
    
    $SUDO_CMD chmod +x $PROJECT_DIR/start_bot.sh
    $SUDO_CMD chown $USER_NAME:$USER_NAME $PROJECT_DIR/start_bot.sh
    
    log_success "启动脚本创建完成"
}

# 创建系统服务
create_systemd_service() {
    log_info "⚙️ 创建系统服务..."
    
    $SUDO_CMD tee /etc/systemd/system/$PROJECT_NAME.service > /dev/null <<EOF
[Unit]
Description=Telegram Bot Service
After=network.target redis-server.service

[Service]
Type=simple
User=$USER_NAME
Group=$USER_NAME
WorkingDirectory=$PROJECT_DIR
ExecStart=$PROJECT_DIR/venv/bin/python $PROJECT_DIR/bot.py
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOF
    
    $SUDO_CMD systemctl daemon-reload
    $SUDO_CMD systemctl enable $PROJECT_NAME
    
    log_success "系统服务创建完成"
}

# 配置防火墙
configure_firewall() {
    log_info "🔥 配置防火墙..."
    
    if [ "$PKG_MANAGER" = "apt" ]; then
        $SUDO_CMD ufw --force enable
        $SUDO_CMD ufw default deny incoming
        $SUDO_CMD ufw default allow outgoing
        $SUDO_CMD ufw allow ssh
        $SUDO_CMD ufw allow 80/tcp
        $SUDO_CMD ufw allow 443/tcp
        $SUDO_CMD ufw allow 8443/tcp
    elif [ "$PKG_MANAGER" = "yum" ]; then
        $SUDO_CMD systemctl enable firewalld
        $SUDO_CMD systemctl start firewalld
        $SUDO_CMD firewall-cmd --permanent --add-service=ssh
        $SUDO_CMD firewall-cmd --permanent --add-service=http
        $SUDO_CMD firewall-cmd --permanent --add-service=https
        $SUDO_CMD firewall-cmd --permanent --add-port=8443/tcp
        $SUDO_CMD firewall-cmd --reload
    fi
    
    log_success "防火墙配置完成"
}

# 创建配置文件模板
create_config_templates() {
    log_info "📝 创建配置文件模板..."
    
    # 创建.env文件模板
    if [ ! -f $PROJECT_DIR/.env ]; then
        cat > $PROJECT_DIR/.env << 'EOF'
# Telegram Bot 配置
BOT_TOKEN=your_bot_token_here
ADMIN_IDS=123456789,987654321
SUPER_ADMIN_ID=123456789

# 数据库配置
DATABASE_URL=sqlite:///data/bot.db

# Redis配置
REDIS_URL=redis://localhost:6379/0

# Webhook配置（可选）
WEBHOOK_URL=https://your-domain.com:8443
WEBHOOK_PORT=8443

# 日志配置
LOG_LEVEL=INFO
LOG_FILE=logs/bot.log
EOF
        
        log_warning "请编辑 $PROJECT_DIR/.env 文件，设置正确的Bot Token"
    fi
    
    log_success "配置文件模板创建完成"
}

# 启动服务
start_services() {
    log_info "🚀 启动服务..."
    
    $SUDO_CMD systemctl start $PROJECT_NAME
    $SUDO_CMD systemctl start redis-server 2>/dev/null || $SUDO_CMD systemctl start redis 2>/dev/null
    $SUDO_CMD systemctl start nginx
    
    # 等待服务启动
    sleep 5
    
    # 检查服务状态
    if systemctl is-active --quiet $PROJECT_NAME; then
        log_success "Bot服务启动成功"
    else
        log_error "Bot服务启动失败"
        $SUDO_CMD systemctl status $PROJECT_NAME
    fi
    
    log_success "所有服务启动完成"
}

# 显示部署信息
show_deployment_info() {
    log_success "🎉 部署完成！"
    echo ""
    echo "📁 项目目录: $PROJECT_DIR"
    echo "👤 服务用户: $USER_NAME"
    echo "🌐 访问地址: http://$(hostname -I | awk '{print $1}')"
    echo "🔧 管理命令:"
    echo "   - 查看状态: $SUDO_CMD systemctl status $PROJECT_NAME"
    echo "   - 启动服务: $SUDO_CMD systemctl start $PROJECT_NAME"
    echo "   - 停止服务: $SUDO_CMD systemctl stop $PROJECT_NAME"
    echo "   - 重启服务: $SUDO_CMD systemctl restart $PROJECT_NAME"
    echo "   - 查看日志: $SUDO_CMD journalctl -u $PROJECT_NAME -f"
    echo ""
    echo "📋 下一步操作:"
    echo "1. 编辑配置文件: $PROJECT_DIR/.env"
    echo "2. 设置Bot Token"
    echo "3. 测试Bot功能"
    echo "4. 配置SSL证书（生产环境）"
    echo ""
    echo "⚠️  注意事项:"
    echo "- 请确保配置文件中的Bot Token正确"
    echo "- 生产环境建议使用正式的SSL证书"
    echo "- 定期检查日志和监控信息"
    echo "- 定期备份重要数据"
}

# 主函数
main() {
    echo ""
    echo "🚀 Telegram Bot 懒人版一键部署脚本 v$PROJECT_VERSION"
    echo "=================================================="
    echo ""
    
    # 检查环境
    detect_system
    check_permissions
    
    log_info "开始部署..."
    echo ""
    
    # 执行部署步骤
    update_system
    install_basic_deps
    install_redis
    install_nginx
    create_project_dirs
    copy_project_files
    create_python_env
    create_startup_script
    create_systemd_service
    configure_firewall
    create_config_templates
    start_services
    
    echo ""
    show_deployment_info
}

# 运行主函数
main "$@"