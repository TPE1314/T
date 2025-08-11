# Telegram Bot 部署指南

本文档详细介绍了如何部署和运行 Telegram Bot 的多种方式。

## 📋 目录

- [系统要求](#系统要求)
- [快速开始](#快速开始)
- [Docker 部署](#docker-部署)
- [手动部署](#手动部署)
- [配置说明](#配置说明)
- [故障排除](#故障排除)
- [生产环境部署](#生产环境部署)

## 🖥️ 系统要求

### 最低要求
- **操作系统**: Linux (Ubuntu 18.04+), macOS 10.14+, Windows 10+
- **Python**: 3.8+
- **内存**: 512MB RAM
- **存储**: 1GB 可用空间
- **网络**: 稳定的互联网连接

### 推荐配置
- **操作系统**: Ubuntu 20.04 LTS 或 CentOS 8+
- **Python**: 3.11+
- **内存**: 2GB+ RAM
- **存储**: 10GB+ 可用空间
- **网络**: 高带宽、低延迟连接

## 🚀 快速开始

### 方法1: 使用一键启动脚本

#### Linux/macOS
```bash
# 下载项目
git clone <your-repo-url>
cd telegram-bot

# 运行快速启动脚本
./quick_start.sh
```

#### Windows
```cmd
# 下载项目
git clone <your-repo-url>
cd telegram-bot

# 运行快速启动脚本
quick_start.bat
```

### 方法2: 使用 Docker（推荐）

#### Linux/macOS
```bash
# 下载项目
git clone <your-repo-url>
cd telegram-bot

# 运行 Docker 部署脚本
./docker_deploy.sh
```

#### Windows
```cmd
# 下载项目
git clone <your-repo-url>
cd telegram-bot

# 运行 Docker 部署脚本
docker_deploy.bat
```

## 🐳 Docker 部署

### 前置条件
1. 安装 [Docker](https://docs.docker.com/get-docker/)
2. 安装 [Docker Compose](https://docs.docker.com/compose/install/)

### 部署步骤

#### 1. 配置环境变量
```bash
# 复制配置文件模板
cp env_example.txt .env

# 编辑配置文件
nano .env  # Linux/macOS
# 或
notepad .env  # Windows
```

#### 2. 启动服务
```bash
# 启动所有服务
./docker_deploy.sh start

# 或使用 docker-compose 直接启动
docker-compose up -d
```

#### 3. 检查服务状态
```bash
# 查看容器状态
docker-compose ps

# 查看服务日志
docker-compose logs -f telegram-bot

# 检查健康状态
curl http://localhost/health
```

### Docker 服务架构

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Nginx (80/443)│    │  Telegram Bot   │    │     Redis      │
│   (反向代理)     │◄──►│   (8443)        │◄──►│    (6379)      │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Prometheus    │    │   PostgreSQL    │    │   监控面板      │
│   (9090)        │    │   (5432)        │    │   (可选)        │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

### 服务端口说明

| 服务 | 端口 | 说明 |
|------|------|------|
| Nginx | 80/443 | HTTP/HTTPS 反向代理 |
| Telegram Bot | 8443 | Bot API 服务 |
| Redis | 6379 | 缓存服务 |
| PostgreSQL | 5432 | 数据库服务 |
| Prometheus | 9090 | 监控服务 |

## 🔧 手动部署

### 1. 安装 Python 依赖

```bash
# 创建虚拟环境
python3 -m venv venv

# 激活虚拟环境
source venv/bin/activate  # Linux/macOS
# 或
venv\Scripts\activate.bat  # Windows

# 安装依赖
pip install -r requirements.txt
```

### 2. 配置环境变量

```bash
# 复制配置文件
cp env_example.txt .env

# 编辑配置文件
nano .env
```

### 3. 创建必要目录

```bash
mkdir -p uploads data updates backups logs
```

### 4. 启动机器人

```bash
# 轮询模式（开发/测试）
python start_bot.py --mode polling

# Webhook模式（生产环境）
python start_bot.py --mode webhook --port 8443
```

## ⚙️ 配置说明

### 环境变量配置

#### 基本配置
```bash
# Bot 配置
BOT_TOKEN=your_bot_token_here
WEBHOOK_URL=https://your-domain.com/webhook

# 管理员配置
ADMIN_IDS=123456789,987654321
SUPER_ADMIN_ID=123456789

# 私聊配置
ENABLE_PRIVATE_CHAT=true
MAX_PRIVATE_CHATS_PER_ADMIN=10
```

#### 数据库配置
```bash
# SQLite（默认）
DATABASE_URL=data/bot.db

# PostgreSQL（可选）
DATABASE_URL=postgresql://user:password@localhost:5432/telegram_bot
```

#### 更新配置
```bash
# 更新服务器
UPDATE_CHECK_URL=https://your-update-server.com/updates
AUTO_UPDATE=false
UPDATE_INTERVAL=3600
```

#### 文件格式配置
```bash
# 支持的文件格式
SUPPORTED_PHOTO_FORMATS=jpg,jpeg,png,gif
SUPPORTED_VIDEO_FORMATS=mp4,avi,mov
SUPPORTED_AUDIO_FORMATS=mp3,wav
SUPPORTED_DOCUMENT_FORMATS=pdf,doc,docx,txt
```

### 配置文件结构

```
telegram-bot/
├── .env                    # 环境变量配置
├── config.py              # 配置加载模块
├── bot.py                 # 主机器人模块
├── handlers.py            # 消息处理器
├── database.py            # 数据库模块
├── admin_manager.py       # 管理员管理
├── update_manager.py      # 更新管理
├── utils.py               # 工具函数
├── uploads/               # 上传文件目录
├── data/                  # 数据库文件目录
├── updates/               # 更新文件目录
├── backups/               # 备份文件目录
└── logs/                  # 日志文件目录
```

## 🔍 故障排除

### 常见问题

#### 1. Bot Token 无效
```
错误: 401 Unauthorized
```
**解决方案**: 检查 `.env` 文件中的 `BOT_TOKEN` 是否正确

#### 2. 权限不足
```
错误: Permission denied
```
**解决方案**: 确保脚本有执行权限
```bash
chmod +x *.sh *.py
```

#### 3. 端口被占用
```
错误: Address already in use
```
**解决方案**: 更改端口或停止占用端口的服务
```bash
# 查看端口占用
netstat -tulpn | grep :8443

# 停止占用端口的服务
sudo systemctl stop <service-name>
```

#### 4. 数据库连接失败
```
错误: Database connection failed
```
**解决方案**: 检查数据库配置和权限

#### 5. Docker 服务启动失败
```bash
# 查看详细错误信息
docker-compose logs

# 重新构建镜像
docker-compose build --no-cache

# 清理资源后重试
docker-compose down -v
docker system prune -f
```

### 日志查看

#### 应用日志
```bash
# 查看机器人日志
tail -f logs/bot.log

# 查看 Docker 日志
docker-compose logs -f telegram-bot
```

#### 系统日志
```bash
# 查看系统服务日志
sudo journalctl -u telegram-bot -f

# 查看 Docker 服务日志
sudo journalctl -u docker -f
```

## 🏭 生产环境部署

### 安全配置

#### 1. SSL 证书
```bash
# 使用 Let's Encrypt 免费证书
sudo apt install certbot
sudo certbot certonly --standalone -d your-domain.com

# 配置 Nginx
sudo cp ssl/cert.pem /etc/nginx/ssl/
sudo cp ssl/key.pem /etc/nginx/ssl/
```

#### 2. 防火墙配置
```bash
# 只开放必要端口
sudo ufw allow 22/tcp    # SSH
sudo ufw allow 80/tcp    # HTTP
sudo ufw allow 443/tcp   # HTTPS
sudo ufw enable
```

#### 3. 系统服务配置
```bash
# 创建系统服务文件
sudo nano /etc/systemd/system/telegram-bot.service

# 启动服务
sudo systemctl enable telegram-bot
sudo systemctl start telegram-bot
```

### 性能优化

#### 1. 数据库优化
```sql
-- PostgreSQL 优化
ALTER SYSTEM SET shared_buffers = '256MB';
ALTER SYSTEM SET effective_cache_size = '1GB';
ALTER SYSTEM SET maintenance_work_mem = '64MB';
ALTER SYSTEM SET checkpoint_completion_target = 0.9;
```

#### 2. Redis 优化
```bash
# Redis 配置优化
maxmemory 512mb
maxmemory-policy allkeys-lru
save 900 1
save 300 10
save 60 10000
```

#### 3. Nginx 优化
```nginx
# 启用 Gzip 压缩
gzip on;
gzip_vary on;
gzip_min_length 1024;
gzip_comp_level 6;

# 启用缓存
location ~* \.(jpg|jpeg|png|gif|ico|css|js)$ {
    expires 1y;
    add_header Cache-Control "public, immutable";
}
```

### 监控和备份

#### 1. 监控配置
```bash
# 启用 Prometheus 监控
docker-compose up -d monitoring

# 配置告警规则
nano monitoring/alerts.yml
```

#### 2. 备份策略
```bash
# 创建备份脚本
nano backup.sh

# 设置定时备份
crontab -e
0 2 * * * /path/to/backup.sh
```

#### 3. 日志轮转
```bash
# 配置 logrotate
sudo nano /etc/logrotate.d/telegram-bot

# 手动轮转
sudo logrotate -f /etc/logrotate.d/telegram-bot
```

## 📚 更多资源

- [Telegram Bot API 文档](https://core.telegram.org/bots/api)
- [Python Telegram Bot 库](https://python-telegram-bot.readthedocs.io/)
- [Docker 官方文档](https://docs.docker.com/)
- [Nginx 配置指南](https://nginx.org/en/docs/)
- [Redis 配置参考](https://redis.io/topics/config)

## 🤝 获取帮助

如果遇到问题，请：

1. 查看本文档的故障排除部分
2. 检查项目 [Issues](https://github.com/your-repo/issues)
3. 查看应用日志获取详细错误信息
4. 在社区论坛寻求帮助

---

**注意**: 本部署指南适用于生产环境，请根据实际需求调整配置参数。