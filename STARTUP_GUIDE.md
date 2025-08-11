# 🚀 Telegram Bot 快速启动指南

## 🎯 快速开始

这个指南将帮助您在 5 分钟内启动您的 Telegram Bot！

## 📋 前置要求

### 必需条件
- ✅ Python 3.8+ 已安装
- ✅ 有效的 Telegram Bot Token
- ✅ 至少一个管理员用户 ID

### 获取 Bot Token
1. 在 Telegram 中找到 [@BotFather](https://t.me/BotFather)
2. 发送 `/newbot` 命令
3. 按提示设置机器人名称和用户名
4. 复制获得的 Bot Token

### 获取用户 ID
1. 在 Telegram 中找到 [@userinfobot](https://t.me/userinfobot)
2. 发送任意消息
3. 复制您的用户 ID

## 🚀 一键启动（推荐）

### Linux/macOS 用户
```bash
# 下载项目后，在项目目录执行：
./quick_start.sh
```

### Windows 用户
```cmd
# 下载项目后，在项目目录执行：
quick_start.bat
```

## ⚙️ 手动配置启动

### 1. 环境配置
```bash
# 复制配置模板
cp env_example.txt .env

# 编辑配置文件
nano .env  # Linux/macOS
# 或
notepad .env  # Windows
```

### 2. 设置关键配置
```bash
# 在 .env 文件中设置：
BOT_TOKEN=your_bot_token_here
ADMIN_IDS=123456789,987654321
SUPER_ADMIN_ID=123456789
DATABASE_URL=sqlite:///data/bot.db
```

### 3. 安装依赖
```bash
# 创建虚拟环境
python3 -m venv venv

# 激活虚拟环境
source venv/bin/activate  # Linux/macOS
# 或
venv\Scripts\activate  # Windows

# 安装依赖
pip install -r requirements.txt
```

### 4. 启动机器人
```bash
# 轮询模式（推荐开发使用）
python start_bot.py --mode polling

# Webhook 模式（推荐生产使用）
python start_bot.py --mode webhook
```

## 🐳 Docker 部署（生产环境）

### 1. 安装 Docker
```bash
# Ubuntu/Debian
sudo apt update
sudo apt install docker.io docker-compose

# macOS
brew install docker docker-compose

# Windows
# 下载 Docker Desktop
```

### 2. 一键部署
```bash
# Linux/macOS
./docker_deploy.sh

# Windows
docker_deploy.bat
```

### 3. 手动 Docker 部署
```bash
# 构建并启动服务
docker-compose up -d

# 查看服务状态
docker-compose ps

# 查看日志
docker-compose logs -f bot
```

## 🧪 功能测试

### 1. 健康检查
```bash
# 快速检查
python health_check.py --quick

# 完整检查
python health_check.py --full

# 自动修复问题
python health_check.py --full --fix
```

### 2. 功能测试
```bash
# 运行所有测试
python test_bot.py --all

# 运行特定测试
python test_bot.py --config --database --admin

# 详细输出
python test_bot.py --all --verbose
```

## 📱 机器人使用

### 1. 基本命令
- `/start` - 启动机器人
- `/help` - 显示帮助信息
- `/admin` - 管理员功能菜单

### 2. 用户功能
- 发送文本消息 - 机器人会回显
- 发送文件 - 自动保存并通知管理员
- 请求私聊 - 与管理员一对一交流

### 3. 管理员功能
- 回复用户消息
- 查看聊天历史
- 管理用户统计
- 检查系统更新

## 🔧 常见问题解决

### 问题 1: 机器人无响应
```bash
# 检查配置
python health_check.py --quick

# 检查日志
tail -f logs/bot.log

# 验证 Bot Token
curl "https://api.telegram.org/bot<YOUR_BOT_TOKEN>/getMe"
```

### 问题 2: 数据库连接失败
```bash
# 检查数据库文件
ls -la data/

# 重新初始化数据库
rm -f data/bot.db
python start_bot.py --mode polling
```

### 问题 3: 文件上传失败
```bash
# 检查上传目录权限
ls -la uploads/

# 设置正确权限
chmod 755 uploads/
chmod 755 data/
chmod 755 logs/
```

### 问题 4: Docker 服务启动失败
```bash
# 检查 Docker 状态
docker-compose ps

# 查看服务日志
docker-compose logs bot
docker-compose logs redis
docker-compose logs nginx

# 重启服务
docker-compose restart
```

## 📊 监控和维护

### 1. 服务状态监控
```bash
# Docker 服务状态
docker-compose ps

# 系统资源使用
docker stats

# 日志监控
docker-compose logs -f --tail=100
```

### 2. 数据备份
```bash
# 备份数据库
cp data/bot.db backup/bot_$(date +%Y%m%d_%H%M%S).db

# 备份上传文件
tar -czf backup/uploads_$(date +%Y%m%d_%H%M%S).tar.gz uploads/
```

### 3. 系统更新
```bash
# 检查更新
curl -s https://api.github.com/repos/your-repo/releases/latest

# 拉取最新代码
git pull origin main

# 重启服务
docker-compose restart bot
```

## 🎯 下一步

### 1. 自定义功能
- 修改 `handlers.py` 添加新命令
- 在 `config.py` 中添加新配置项
- 扩展 `database.py` 添加新数据表

### 2. 生产部署
- 配置 SSL 证书
- 设置防火墙规则
- 配置监控告警
- 设置自动备份

### 3. 性能优化
- 启用 Redis 缓存
- 配置数据库连接池
- 优化文件存储策略
- 添加负载均衡

## 📞 获取帮助

### 1. 查看文档
- [README.md](README.md) - 项目介绍
- [DEPLOYMENT.md](DEPLOYMENT.md) - 部署指南
- [PROJECT_SUMMARY.md](PROJECT_SUMMARY.md) - 功能总结

### 2. 运行诊断
```bash
# 完整系统检查
python health_check.py --full --verbose

# 功能测试
python test_bot.py --all --verbose
```

### 3. 查看日志
```bash
# 机器人日志
tail -f logs/bot.log

# Docker 日志
docker-compose logs -f bot

# 系统日志
journalctl -u docker.service -f
```

## 🎉 恭喜！

您已经成功启动了您的 Telegram Bot！🎉

现在您可以：
- 📱 在 Telegram 中与机器人对话
- 🔧 使用管理员功能管理机器人
- 📊 监控机器人运行状态
- 🚀 根据需要扩展功能

祝您使用愉快！如果遇到问题，请参考本文档或运行健康检查脚本。

---

**快速启动完成时间**: 约 5 分钟  
**推荐部署方式**: 一键启动脚本  
**生产环境**: Docker 部署  
**监控工具**: 内置健康检查脚本