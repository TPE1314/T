# Ubuntu 一键部署安装脚本使用说明

## 📋 概述

本项目提供了两个Ubuntu部署脚本，用于在Ubuntu系统上快速部署Telegram Bot服务：

1. **`ubuntu_deploy.sh`** - 完整版部署脚本（推荐生产环境）
2. **`quick_deploy.sh`** - 快速部署脚本（适合开发测试）

## 🚀 快速开始

### 前置要求

- Ubuntu 18.04 或更高版本
- 普通用户账户（非root用户）
- 网络连接
- sudo权限

### 方法1：快速部署（推荐新手）

```bash
# 下载脚本
wget https://raw.githubusercontent.com/your-repo/your-project/main/quick_deploy.sh

# 添加执行权限
chmod +x quick_deploy.sh

# 运行部署脚本
./quick_deploy.sh
```

### 方法2：完整部署（推荐生产环境）

```bash
# 下载脚本
wget https://raw.githubusercontent.com/your-repo/your-project/main/ubuntu_deploy.sh

# 添加执行权限
chmod +x ubuntu_deploy.sh

# 运行部署脚本
./ubuntu_deploy.sh
```

## 🔧 脚本功能对比

| 功能 | 快速部署 | 完整部署 |
|------|----------|----------|
| 系统依赖安装 | ✅ 基础 | ✅ 完整 |
| Python环境 | ✅ 基础 | ✅ 完整 |
| Redis | ✅ | ✅ |
| Nginx | ✅ 基础 | ✅ 完整配置 |
| MySQL | ❌ | ✅ 可选 |
| MongoDB | ❌ | ✅ 可选 |
| Docker | ❌ | ✅ 可选 |
| 系统服务 | ✅ | ✅ |
| 防火墙配置 | ✅ 基础 | ✅ 完整 |
| 日志轮转 | ❌ | ✅ |
| 备份脚本 | ❌ | ✅ |
| 监控脚本 | ❌ | ✅ |
| 安全配置 | ❌ | ✅ |

## 📁 部署后的目录结构

```
/home/用户名/telegram-bot/
├── app/                    # 应用代码
├── static/                 # 静态文件
├── uploads/                # 上传文件
├── data/                   # 数据文件
├── logs/                   # 日志文件
├── backups/                # 备份文件
├── config/                 # 配置文件
├── ssl/                    # SSL证书
├── venv/                   # Python虚拟环境
├── requirements.txt        # Python依赖
├── bot.py                  # 主程序
├── start_bot.sh           # 启动脚本
├── backup.sh              # 备份脚本（完整版）
└── monitor.sh             # 监控脚本（完整版）
```

## 🛠️ 管理命令

### 服务管理

```bash
# 查看服务状态
sudo systemctl status telegram-bot

# 启动服务
sudo systemctl start telegram-bot

# 停止服务
sudo systemctl stop telegram-bot

# 重启服务
sudo systemctl restart telegram-bot

# 查看日志
sudo journalctl -u telegram-bot -f
```

### 其他服务

```bash
# Redis状态
sudo systemctl status redis-server

# Nginx状态
sudo systemctl status nginx

# 防火墙状态
sudo ufw status
```

## ⚙️ 配置说明

### 1. 环境变量配置

部署完成后，需要配置 `.env` 文件：

```bash
# 编辑配置文件
nano /home/用户名/telegram-bot/.env

# 主要配置项
BOT_TOKEN=your_bot_token_here
ADMIN_IDS=123456789,987654321
SUPER_ADMIN_ID=123456789
```

### 2. Bot配置

编辑 `config.py` 文件：

```python
# 数据库配置
DATABASE_URL = "sqlite:///data/bot.db"

# Redis配置
REDIS_URL = "redis://localhost:6379/0"

# 其他配置...
```

### 3. Nginx配置（完整版）

完整版会自动配置Nginx，包括：
- 反向代理到Bot API
- 静态文件服务
- 上传文件服务
- 健康检查端点

## 🔒 安全配置

### 防火墙规则

脚本会自动配置UFW防火墙：
- 允许SSH连接
- 允许HTTP/HTTPS
- 允许Bot API端口
- 默认拒绝入站连接

### 服务用户

完整版会创建专用的服务用户 `botuser`，提高安全性。

## 📊 监控和维护

### 自动备份

完整版包含自动备份功能：
- 每日凌晨2点自动备份
- 保留最近30天的备份
- 备份数据、上传文件、日志等

### 系统监控

完整版包含监控脚本：
- 每5分钟检查服务状态
- 监控磁盘和内存使用
- 自动重启失败的服务

### 日志管理

- 自动日志轮转
- 日志压缩和清理
- 系统日志集成

## 🚨 故障排除

### 常见问题

1. **服务启动失败**
   ```bash
   # 查看详细错误信息
   sudo journalctl -u telegram-bot -n 50
   
   # 检查配置文件
   sudo systemctl status telegram-bot
   ```

2. **权限问题**
   ```bash
   # 修复文件权限
   sudo chown -R 用户名:用户名 /home/用户名/telegram-bot/
   sudo chmod -R 755 /home/用户名/telegram-bot/
   ```

3. **端口冲突**
   ```bash
   # 检查端口占用
   sudo netstat -tlnp | grep :8443
   sudo netstat -tlnp | grep :80
   ```

4. **Redis连接失败**
   ```bash
   # 检查Redis状态
   sudo systemctl status redis-server
   
   # 测试Redis连接
   redis-cli ping
   ```

### 日志位置

- 应用日志：`/home/用户名/telegram-bot/logs/`
- 系统日志：`/var/log/syslog`
- Nginx日志：`/var/log/nginx/`
- Redis日志：`/var/log/redis/`

## 🔄 更新和升级

### 更新代码

```bash
cd /home/用户名/telegram-bot/
git pull origin main
sudo systemctl restart telegram-bot
```

### 更新依赖

```bash
cd /home/用户名/telegram-bot/
source venv/bin/activate
pip install -r requirements.txt --upgrade
sudo systemctl restart telegram-bot
```

### 系统升级

```bash
sudo apt update && sudo apt upgrade -y
sudo systemctl restart telegram-bot
```

## 📞 技术支持

如果遇到问题，请：

1. 检查日志文件
2. 查看服务状态
3. 确认配置文件正确
4. 检查网络连接
5. 查看系统资源使用情况

## 📝 更新日志

- **v1.0.0** - 初始版本，支持基础部署
- **v1.1.0** - 添加完整版部署脚本
- **v1.2.0** - 增强安全配置和监控功能

## ⚠️ 注意事项

1. **不要使用root用户运行脚本**
2. **生产环境建议使用完整版脚本**
3. **定期备份重要数据**
4. **及时更新系统和依赖**
5. **监控系统资源使用情况**
6. **配置SSL证书（生产环境）**

## 📄 许可证

本项目采用 MIT 许可证，详见 LICENSE 文件。