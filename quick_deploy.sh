#!/bin/bash

# Ubuntu 快速部署脚本
# 简化版本，只安装必要的组件

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

# 检查是否为root用户
if [ "$EUID" -eq 0 ]; then
    log_error "请不要使用root用户运行此脚本"
    exit 1
fi

log_info "🚀 开始快速部署..."

# 更新系统
log_info "更新系统包..."
sudo apt update && sudo apt upgrade -y

# 安装基础依赖
log_info "安装基础依赖..."
sudo apt install -y \
    python3 \
    python3-pip \
    python3-venv \
    python3-dev \
    redis-server \
    nginx \
    curl \
    git \
    supervisor \
    ufw

# 配置Redis
log_info "配置Redis..."
sudo sed -i 's/bind 127.0.0.1/bind 0.0.0.0/' /etc/redis/redis.conf
sudo systemctl enable redis-server
sudo systemctl start redis-server

# 配置Nginx
log_info "配置Nginx..."
sudo systemctl enable nginx
sudo systemctl start nginx

# 创建项目目录
PROJECT_DIR="/home/$(whoami)/telegram-bot"
log_info "创建项目目录: $PROJECT_DIR"
mkdir -p $PROJECT_DIR/{logs,uploads,data,backups}

# 复制项目文件
log_info "复制项目文件..."
cp -r * $PROJECT_DIR/
cd $PROJECT_DIR

# 创建Python虚拟环境
log_info "创建Python虚拟环境..."
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

# 创建启动脚本
log_info "创建启动脚本..."
cat > start_bot.sh << 'EOF'
#!/bin/bash
cd /home/$(whoami)/telegram-bot
source venv/bin/activate
python bot.py
EOF

chmod +x start_bot.sh

# 创建系统服务
log_info "创建系统服务..."
sudo tee /etc/systemd/system/telegram-bot.service > /dev/null <<EOF
[Unit]
Description=Telegram Bot Service
After=network.target redis-server.service

[Service]
Type=simple
User=$(whoami)
WorkingDirectory=$PROJECT_DIR
ExecStart=$PROJECT_DIR/venv/bin/python $PROJECT_DIR/bot.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# 启用并启动服务
sudo systemctl daemon-reload
sudo systemctl enable telegram-bot
sudo systemctl start telegram-bot

# 配置防火墙
log_info "配置防火墙..."
sudo ufw --force enable
sudo ufw allow ssh
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp

log_success "🎉 快速部署完成！"
echo ""
echo "📁 项目目录: $PROJECT_DIR"
echo "🌐 访问地址: http://$(hostname -I | awk '{print $1}')"
echo "🔧 管理命令:"
echo "   - 查看状态: sudo systemctl status telegram-bot"
echo "   - 启动服务: sudo systemctl start telegram-bot"
echo "   - 停止服务: sudo systemctl stop telegram-bot"
echo "   - 查看日志: sudo journalctl -u telegram-bot -f"
echo ""
echo "⚠️  下一步操作:"
echo "1. 编辑配置文件: $PROJECT_DIR/config.py"
echo "2. 设置环境变量: $PROJECT_DIR/.env"
echo "3. 测试Bot功能"