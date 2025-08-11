#!/bin/bash

# Ubuntu 一键部署安装脚本
# 适用于 Ubuntu 18.04+ 系统
# 自动安装系统依赖、Python环境、Redis、Nginx等

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# 配置变量
PYTHON_VERSION="3.11"
PROJECT_NAME="telegram-bot"
USER_NAME=$(whoami)
PROJECT_DIR="/home/$USER_NAME/$PROJECT_NAME"
SERVICE_USER="botuser"
SERVICE_GROUP="botgroup"

# 根据用户类型决定是否使用sudo
SUDO_CMD="sudo"

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

log_step() {
    echo -e "${PURPLE}[STEP]${NC} $1"
}

# 检查是否为root用户
check_root() {
    if [ "$EUID" -eq 0 ]; then
        log_warning "检测到root用户，将使用root权限进行部署"
        log_info "注意：生产环境建议使用普通用户+sudo权限"
        read -p "是否继续？(y/N): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            log_info "部署已取消"
            exit 0
        fi
        # 设置root用户相关变量
        USER_NAME="root"
        PROJECT_DIR="/root/$PROJECT_NAME"
        SERVICE_USER="root"
        SERVICE_GROUP="root"
        SUDO_CMD=""
    fi
}

# 检查Ubuntu版本
check_ubuntu_version() {
    log_step "检查Ubuntu版本..."
    
    if ! command -v lsb_release &> /dev/null; then
        log_warning "无法检测Ubuntu版本，继续执行..."
        return
    fi
    
    UBUNTU_VERSION=$(lsb_release -rs)
    UBUNTU_MAJOR=$(echo $UBUNTU_VERSION | cut -d. -f1)
    
    if [ "$UBUNTU_MAJOR" -lt "18" ]; then
        log_warning "检测到Ubuntu $UBUNTU_VERSION，建议使用Ubuntu 18.04或更高版本"
        read -p "是否继续？(y/N): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            exit 1
        fi
    else
        log_success "Ubuntu版本检查通过: $UBUNTU_VERSION"
    fi
}

# 更新系统包
update_system() {
    log_step "更新系统包..."
    
    $SUDO_CMD apt update
    $SUDO_CMD apt upgrade -y
    
    log_success "系统包更新完成"
}

# 安装基础依赖
install_basic_deps() {
    log_step "安装基础依赖包..."
    
    $SUDO_CMD apt install -y \
        curl \
        wget \
        git \
        vim \
        nano \
        htop \
        unzip \
        zip \
        build-essential \
        software-properties-common \
        apt-transport-https \
        ca-certificates \
        gnupg \
        lsb-release \
        ufw \
        fail2ban \
        logrotate \
        supervisor \
        cron \
        rsyslog
    
    log_success "基础依赖安装完成"
}

# 安装Python相关依赖
install_python_deps() {
    log_step "安装Python相关依赖..."
    
    $SUDO_CMD apt install -y \
        python3 \
        python3-pip \
        python3-venv \
        python3-dev \
        python3-setuptools \
        python3-wheel \
        python3-cffi \
        python3-cryptography \
        python3-openssl \
        python3-requests \
        python3-yaml \
        python3-psutil \
        python3-pil \
        python3-pil.imagetk \
        python3-dateutil \
        python3-colorlog \
        python3-aiofiles \
        python3-redis \
        python3-sqlite3 \
        python3-mysqldb \
        python3-pymongo \
        python3-elasticsearch \
        python3-kafka \
        python3-celery \
        python3-flower \
        python3-gunicorn \
        python3-uwsgi \
        python3-nginx \
        python3-supervisor
    
    # 升级pip
    python3 -m pip install --upgrade pip
    
    log_success "Python依赖安装完成"
}

# 安装Redis
install_redis() {
    log_step "安装Redis..."
    
    $SUDO_CMD apt install -y redis-server
    
    # 配置Redis
    $SUDO_CMD sed -i 's/bind 127.0.0.1/bind 0.0.0.0/' /etc/redis/redis.conf
    $SUDO_CMD sed -i 's/# requirepass foobared/requirepass botredis123/' /etc/redis/redis.conf
    $SUDO_CMD sed -i 's/appendonly no/appendonly yes/' /etc/redis/redis.conf
    
    # 启动Redis
    $SUDO_CMD systemctl enable redis-server
    $SUDO_CMD systemctl start redis-server
    
    log_success "Redis安装完成"
}

# 安装Nginx
install_nginx() {
    log_step "安装Nginx..."
    
    $SUDO_CMD apt install -y nginx
    
    # 创建Nginx配置
    $SUDO_CMD tee /etc/nginx/sites-available/$PROJECT_NAME > /dev/null <<EOF
server {
    listen 80;
    server_name _;
    
    # 日志
    access_log /var/log/nginx/bot_access.log;
    error_log /var/log/nginx/bot_error.log;
    
    # 静态文件
    location /static/ {
        alias $PROJECT_DIR/static/;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }
    
    # 上传文件
    location /uploads/ {
        alias $PROJECT_DIR/uploads/;
        expires 7d;
        add_header Cache-Control "public";
    }
    
    # 健康检查
    location /health {
        access_log off;
        return 200 "OK\n";
        add_header Content-Type text/plain;
    }
    
    # 反向代理到Bot API
    location /api/ {
        proxy_pass http://127.0.0.1:8443/;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }
    
    # 默认页面
    location / {
        return 200 "Telegram Bot Service\n";
        add_header Content-Type text/plain;
    }
}
EOF
    
    # 启用站点
    $SUDO_CMD ln -sf /etc/nginx/sites-available/$PROJECT_NAME /etc/nginx/sites-enabled/
    $SUDO_CMD rm -f /etc/nginx/sites-enabled/default
    
    # 测试配置
    $SUDO_CMD nginx -t
    
    # 启动Nginx
    $SUDO_CMD systemctl enable nginx
    $SUDO_CMD systemctl start nginx
    
    log_success "Nginx安装完成"
}

# 安装MySQL（可选）
install_mysql() {
    read -p "是否安装MySQL？(y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        log_step "安装MySQL..."
        
        $SUDO_CMD apt install -y mysql-server
        
        # 安全配置
        $SUDO_CMD mysql_secure_installation
        
        # 创建数据库和用户
        $SUDO_CMD mysql -e "CREATE DATABASE IF NOT EXISTS botdb CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"
        $SUDO_CMD mysql -e "CREATE USER IF NOT EXISTS 'botuser'@'localhost' IDENTIFIED BY 'botpass123';"
        $SUDO_CMD mysql -e "GRANT ALL PRIVILEGES ON botdb.* TO 'botuser'@'localhost';"
        $SUDO_CMD mysql -e "FLUSH PRIVILEGES;"
        
        log_success "MySQL安装完成"
    fi
}

# 安装MongoDB（可选）
install_mongodb() {
    read -p "是否安装MongoDB？(y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        log_step "安装MongoDB..."
        
        # 添加MongoDB官方源
        wget -qO - https://www.mongodb.org/static/pgp/server-6.0.asc | $SUDO_CMD apt-key add -
        echo "deb [ arch=amd64,arm64 ] https://repo.mongodb.org/apt/ubuntu focal/mongodb-org/6.0 multiverse" | $SUDO_CMD tee /etc/apt/sources.list.d/mongodb-org-6.0.list
        
        $SUDO_CMD apt update
        $SUDO_CMD apt install -y mongodb-org
        
        # 启动MongoDB
        $SUDO_CMD systemctl enable mongod
        $SUDO_CMD systemctl start mongod
        
        log_success "MongoDB安装完成"
    fi
}

# 安装Docker（可选）
install_docker() {
    read -p "是否安装Docker？(y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        log_step "安装Docker..."
        
        # 安装Docker
        curl -fsSL https://get.docker.com -o get-docker.sh
        $SUDO_CMD sh get-docker.sh
        
        # 添加用户到docker组
        $SUDO_CMD usermod -aG docker $USER_NAME
        
        # 安装Docker Compose
        $SUDO_CMD curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -m)" -o /usr/local/bin/docker-compose
        $SUDO_CMD chmod +x /usr/local/bin/docker-compose
        
        # 启动Docker
        $SUDO_CMD systemctl enable docker
        $SUDO_CMD systemctl start docker
        
        log_success "Docker安装完成"
        log_warning "请重新登录以使docker组权限生效"
    fi
}

# 创建项目用户
create_project_user() {
    log_step "创建项目用户..."
    
    if ! id "$SERVICE_USER" &>/dev/null; then
        $SUDO_CMD useradd -r -s /bin/bash -d $PROJECT_DIR $SERVICE_USER
        $SUDO_CMD usermod -aG $SERVICE_USER $USER_NAME
        log_success "项目用户创建完成: $SERVICE_USER"
    else
        log_info "项目用户已存在: $SERVICE_USER"
    fi
}

# 创建项目目录
create_project_dirs() {
    log_step "创建项目目录..."
    
    $SUDO_CMD mkdir -p $PROJECT_DIR/{app,static,uploads,data,logs,backups,config,ssl}
    $SUDO_CMD chown -R $SERVICE_USER:$SERVICE_USER $PROJECT_DIR
    $SUDO_CMD chmod -R 755 $PROJECT_DIR
    
    log_success "项目目录创建完成"
}

# 创建Python虚拟环境
create_python_env() {
    log_step "创建Python虚拟环境..."
    
    cd $PROJECT_DIR
    $SUDO_CMD -u $SERVICE_USER python3 -m venv venv
    $SUDO_CMD -u $SERVICE_USER $PROJECT_DIR/venv/bin/pip install --upgrade pip
    
    log_success "Python虚拟环境创建完成"
}

# 安装Python依赖
install_python_requirements() {
    log_step "安装Python依赖..."
    
    cd $PROJECT_DIR
    $SUDO_CMD -u $SERVICE_USER $PROJECT_DIR/venv/bin/pip install -r requirements.txt
    
    log_success "Python依赖安装完成"
}

# 创建系统服务
create_systemd_service() {
    log_step "创建系统服务..."
    
    $SUDO_CMD tee /etc/systemd/system/$PROJECT_NAME.service > /dev/null <<EOF
[Unit]
Description=Telegram Bot Service
After=network.target redis-server.service
Wants=redis-server.service

[Service]
Type=simple
User=$SERVICE_USER
Group=$SERVICE_USER
WorkingDirectory=$PROJECT_DIR
Environment=PATH=$PROJECT_DIR/venv/bin
ExecStart=$PROJECT_DIR/venv/bin/python $PROJECT_DIR/bot.py
ExecReload=/bin/kill -HUP \$MAINPID
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal
SyslogIdentifier=$PROJECT_NAME

# 安全设置
NoNewPrivileges=true
PrivateTmp=true
ProtectSystem=strict
ProtectHome=true
ReadWritePaths=$PROJECT_DIR

[Install]
WantedBy=multi-user.target
EOF
    
    # 重新加载systemd
    $SUDO_CMD systemctl daemon-reload
    $SUDO_CMD systemctl enable $PROJECT_NAME
    
    log_success "系统服务创建完成"
}

# 创建Supervisor配置
create_supervisor_config() {
    log_step "创建Supervisor配置..."
    
    $SUDO_CMD tee /etc/supervisor/conf.d/$PROJECT_NAME.conf > /dev/null <<EOF
[program:$PROJECT_NAME]
command=$PROJECT_DIR/venv/bin/python $PROJECT_DIR/bot.py
directory=$PROJECT_DIR
user=$SERVICE_USER
autostart=true
autorestart=true
redirect_stderr=true
stdout_logfile=$PROJECT_DIR/logs/bot.log
stdout_logfile_maxbytes=50MB
stdout_logfile_backups=10
stderr_logfile=$PROJECT_DIR/logs/bot_error.log
stderr_logfile_maxbytes=50MB
stderr_logfile_backups=10
environment=PATH="$PROJECT_DIR/venv/bin"
EOF
    
    # 重新加载Supervisor
    $SUDO_CMD supervisorctl reread
    $SUDO_CMD supervisorctl update
    
    log_success "Supervisor配置创建完成"
}

# 配置防火墙
configure_firewall() {
    log_step "配置防火墙..."
    
    sudo ufw --force enable
    sudo ufw default deny incoming
    sudo ufw default allow outgoing
    sudo ufw allow ssh
    sudo ufw allow 80/tcp
    sudo ufw allow 443/tcp
    sudo ufw allow 8443/tcp
    
    log_success "防火墙配置完成"
}

# 配置日志轮转
configure_logrotate() {
    log_step "配置日志轮转..."
    
    sudo tee /etc/logrotate.d/$PROJECT_NAME > /dev/null <<EOF
$PROJECT_DIR/logs/*.log {
    daily
    missingok
    rotate 30
    compress
    delaycompress
    notifempty
    create 644 $SERVICE_USER $SERVICE_USER
    postrotate
        systemctl reload $PROJECT_NAME > /dev/null 2>&1 || true
    endscript
}
EOF
    
    log_success "日志轮转配置完成"
}

# 创建备份脚本
create_backup_script() {
    log_step "创建备份脚本..."
    
    sudo tee $PROJECT_DIR/backup.sh > /dev/null <<EOF
#!/bin/bash
# 备份脚本

BACKUP_DIR="$PROJECT_DIR/backups"
DATE=\$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="backup_\$DATE.tar.gz"

cd $PROJECT_DIR
tar -czf "\$BACKUP_DIR/\$BACKUP_FILE" data uploads logs config

# 保留最近30天的备份
find \$BACKUP_DIR -name "backup_*.tar.gz" -mtime +30 -delete

echo "备份完成: \$BACKUP_FILE"
EOF
    
    sudo chmod +x $PROJECT_DIR/backup.sh
    sudo chown $SERVICE_USER:$SERVICE_USER $PROJECT_DIR/backup.sh
    
    # 添加到crontab
    (sudo crontab -l 2>/dev/null; echo "0 2 * * * $PROJECT_DIR/backup.sh") | sudo crontab -
    
    log_success "备份脚本创建完成"
}

# 创建监控脚本
create_monitoring_script() {
    log_step "创建监控脚本..."
    
    sudo tee $PROJECT_DIR/monitor.sh > /dev/null <<EOF
#!/bin/bash
# 监控脚本

LOG_FILE="$PROJECT_DIR/logs/monitor.log"
DATE=\$(date '+%Y-%m-%d %H:%M:%S')

# 检查服务状态
if ! systemctl is-active --quiet $PROJECT_NAME; then
    echo "[\$DATE] 服务未运行，尝试重启..." >> \$LOG_FILE
    systemctl restart $PROJECT_NAME
fi

# 检查Redis状态
if ! systemctl is-active --quiet redis-server; then
    echo "[\$DATE] Redis未运行，尝试重启..." >> \$LOG_FILE
    systemctl restart redis-server
fi

# 检查磁盘空间
DISK_USAGE=\$(df / | tail -1 | awk '{print \$5}' | sed 's/%//')
if [ \$DISK_USAGE -gt 80 ]; then
    echo "[\$DATE] 磁盘使用率过高: \$DISK_USAGE%" >> \$LOG_FILE
fi

# 检查内存使用
MEM_USAGE=\$(free | grep Mem | awk '{printf("%.0f", \$3/\$2 * 100.0)}')
if [ \$MEM_USAGE -gt 80 ]; then
    echo "[\$DATE] 内存使用率过高: \$MEM_USAGE%" >> \$LOG_FILE
fi
EOF
    
    sudo chmod +x $PROJECT_DIR/monitor.sh
    sudo chown $SERVICE_USER:$SERVICE_USER $PROJECT_DIR/monitor.sh
    
    # 添加到crontab，每5分钟检查一次
    (sudo crontab -l 2>/dev/null; echo "*/5 * * * * $PROJECT_DIR/monitor.sh") | sudo crontab -
    
    log_success "监控脚本创建完成"
}

# 复制项目文件
copy_project_files() {
    log_step "复制项目文件..."
    
    # 获取当前脚本所在目录
    SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
    
    # 复制项目文件
    sudo cp -r $SCRIPT_DIR/* $PROJECT_DIR/
    sudo chown -R $SERVICE_USER:$SERVICE_USER $PROJECT_DIR
    
    log_success "项目文件复制完成"
}

# 启动服务
start_services() {
    log_step "启动服务..."
    
    sudo systemctl start $PROJECT_NAME
    sudo systemctl start redis-server
    sudo systemctl start nginx
    
    # 等待服务启动
    sleep 5
    
    # 检查服务状态
    if systemctl is-active --quiet $PROJECT_NAME; then
        log_success "Bot服务启动成功"
    else
        log_error "Bot服务启动失败"
        sudo systemctl status $PROJECT_NAME
    fi
    
    if systemctl is-active --quiet redis-server; then
        log_success "Redis服务启动成功"
    else
        log_error "Redis服务启动失败"
    fi
    
    if systemctl is-active --quiet nginx; then
        log_success "Nginx服务启动成功"
    else
        log_error "Nginx服务启动失败"
    fi
}

# 显示部署信息
show_deployment_info() {
    log_success "🎉 部署完成！"
    echo ""
    echo "📁 项目目录: $PROJECT_DIR"
    echo "👤 服务用户: $SERVICE_USER"
    echo "🌐 访问地址: http://$(hostname -I | awk '{print $1}')"
    echo "🔧 管理命令:"
    echo "   - 查看状态: sudo systemctl status $PROJECT_NAME"
    echo "   - 启动服务: sudo systemctl start $PROJECT_NAME"
    echo "   - 停止服务: sudo systemctl stop $PROJECT_NAME"
    echo "   - 重启服务: sudo systemctl restart $PROJECT_NAME"
    echo "   - 查看日志: sudo journalctl -u $PROJECT_NAME -f"
    echo "   - 备份数据: $PROJECT_DIR/backup.sh"
    echo ""
    echo "📋 下一步操作:"
    echo "1. 编辑配置文件: $PROJECT_DIR/config.py"
    echo "2. 设置环境变量: $PROJECT_DIR/.env"
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
    log_info "🚀 开始Ubuntu一键部署安装..."
    echo ""
    
    # 检查环境
    check_root
    check_ubuntu_version
    
    # 安装系统依赖
    update_system
    install_basic_deps
    install_python_deps
    install_redis
    install_nginx
    
    # 可选安装
    install_mysql
    install_mongodb
    install_docker
    
    # 项目配置
    create_project_user
    create_project_dirs
    copy_project_files
    create_python_env
    install_python_requirements
    
    # 服务配置
    create_systemd_service
    create_supervisor_config
    configure_firewall
    configure_logrotate
    create_backup_script
    create_monitoring_script
    
    # 启动服务
    start_services
    
    # 显示结果
    show_deployment_info
    
    log_success "🎯 部署脚本执行完成！"
}

# 错误处理
trap 'log_error "脚本执行失败，请检查错误信息"; exit 1' ERR

# 运行主函数
main "$@"