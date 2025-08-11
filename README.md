# 🤖 Telegram 多媒体双向机器人

一个功能完整的Telegram机器人，支持多种多媒体消息类型，具备双向通信能力。

## ✨ 功能特性

### 📱 支持的消息类型
- **图片**: JPG, JPEG, PNG, GIF, WebP
- **视频**: MP4, AVI, MOV, MKV, WebM
- **音频**: MP3, WAV, OGG, M4A, FLAC
- **文档**: PDF, DOC, DOCX, TXT, ZIP, RAR
- **语音消息**: 语音录制
- **贴纸**: 表情贴纸
- **动画**: GIF动画
- **联系人**: 联系人信息
- **位置**: 地理位置

### 🔧 核心功能
- 自动下载并保存多媒体文件
- 智能文件命名和分类
- 文件大小和类型验证
- 用户交互式按钮
- 详细的文件信息显示
- 支持轮询和Webhook两种模式
- **多管理员支持**: 支持多个管理员同时管理机器人
- **私聊选择功能**: 用户可以选择特定管理员进行私聊
- **管理员回复功能**: 管理员可以直接回复用户消息
- **数据库支持**: 使用SQLite数据库存储用户、消息和回复信息
- **云更新系统**: 支持在线检查和自动更新
- **一键安装脚本**: 生成Linux和Windows平台的安装脚本

## 🚀 快速开始

### 方法1：Ubuntu一键部署（推荐）

#### 1. 获取Bot Token
1. 在Telegram中搜索 `@BotFather`
2. 发送 `/newbot` 命令
3. 按提示设置机器人名称和用户名
4. 复制获得的Bot Token

#### 2. 运行部署脚本
```bash
# 快速部署（开发测试）
wget https://raw.githubusercontent.com/your-repo/your-project/main/quick_deploy.sh
chmod +x quick_deploy.sh
./quick_deploy.sh

# 或完整部署（生产环境）
wget https://raw.githubusercontent.com/your-repo/your-project/main/ubuntu_deploy.sh
chmod +x ubuntu_deploy.sh
./ubuntu_deploy.sh
```

#### 3. 配置环境变量
部署完成后，编辑配置文件：
```bash
nano /home/$(whoami)/telegram-bot/.env
```

填入您的Bot Token：
```env
BOT_TOKEN=your_bot_token_here
ADMIN_IDS=your_admin_id
SUPER_ADMIN_ID=your_super_admin_id
```

#### 4. 启动服务
```bash
sudo systemctl start telegram-bot
sudo systemctl enable telegram-bot
```

### 方法2：传统安装

#### 1. 获取Bot Token
1. 在Telegram中搜索 `@BotFather`
2. 发送 `/newbot` 命令
3. 按提示设置机器人名称和用户名
4. 复制获得的Bot Token

#### 2. 安装依赖
```bash
pip install -r requirements.txt
```

#### 3. 配置环境变量
复制 `env_example.txt` 为 `.env` 并填写配置：
```bash
cp env_example.txt .env
```

编辑 `.env` 文件：
```env
BOT_TOKEN=your_bot_token_here
UPLOAD_FOLDER=./uploads
MAX_FILE_SIZE=50
```

#### 4. 运行机器人

##### 轮询模式（推荐用于开发测试）
```bash
python bot.py
```

##### Webhook模式（推荐用于生产环境）
```bash
python webhook_server.py
```

## 📁 项目结构

```
telegram-bot/
├── 📱 核心文件
│   ├── bot.py              # 主机器人文件
│   ├── handlers.py         # 消息处理器
│   ├── config.py           # 配置文件
│   ├── utils.py            # 工具函数
│   ├── admin_manager.py    # 管理员管理器
│   ├── database.py         # 数据库管理
│   ├── update_manager.py   # 更新管理器
│   └── webhook_server.py   # Webhook服务器
│
├── 🚀 部署脚本
│   ├── ubuntu_deploy.sh    # Ubuntu完整部署脚本
│   ├── quick_deploy.sh     # Ubuntu快速部署脚本
│   ├── test_deployment.sh  # 部署测试脚本
│   ├── docker_deploy.sh    # Docker部署脚本
│   └── docker_deploy.bat   # Windows Docker部署脚本
│
├── 📋 配置文件
│   ├── requirements.txt     # Python依赖
│   ├── env_example.txt     # 环境变量示例
│   ├── docker-compose.yml  # Docker Compose配置
│   ├── Dockerfile          # Docker镜像配置
│   └── nginx.conf          # Nginx配置模板
│
├── 📚 文档
│   ├── README.md           # 项目说明
│   ├── UBUNTU_DEPLOY_README.md # Ubuntu部署说明
│   ├── DEPLOYMENT.md       # 部署指南
│   ├── PROJECT_STRUCTURE.md # 项目结构说明
│   └── STARTUP_GUIDE.md    # 启动指南
│
├── 🛠️ 工具脚本
│   ├── start_bot.py        # 启动脚本
│   ├── quick_start.sh      # Linux/macOS快速启动脚本
│   ├── quick_start.bat     # Windows快速启动脚本
│   └── health_check.py     # 健康检查脚本
│
├── 📁 数据目录
│   ├── uploads/            # 文件上传目录
│   ├── data/               # 数据库目录
│   ├── updates/            # 更新文件目录
│   ├── logs/               # 日志文件目录
│   ├── backups/            # 备份文件目录
│   └── monitoring/         # 监控脚本目录
│
└── 🔧 其他文件
    ├── .gitignore          # Git忽略文件
    ├── .dockerignore       # Docker忽略文件
    └── redis.conf          # Redis配置模板
```

## ⚙️ 配置说明

### 环境变量

| 变量名 | 说明 | 默认值 |
|--------|------|--------|
| `BOT_TOKEN` | Telegram Bot Token | 必需 |
| `WEBHOOK_URL` | Webhook URL（Webhook模式） | 可选 |
| `WEBHOOK_PORT` | Webhook端口 | 8443 |
| `UPLOAD_FOLDER` | 文件保存目录 | ./uploads |
| `MAX_FILE_SIZE` | 最大文件大小(MB) | 50 |
| `ADMIN_IDS` | 管理员用户ID列表 | 必需 |
| `SUPER_ADMIN_ID` | 超级管理员用户ID | 必需 |
| `ENABLE_PRIVATE_CHAT` | 启用私聊功能 | true |
| `MAX_PRIVATE_CHATS_PER_ADMIN` | 每个管理员最大私聊数 | 10 |
| `DATABASE_URL` | 数据库文件路径 | data/bot.db |
| `UPDATE_CHECK_URL` | 更新检查URL | 可选 |
| `AUTO_UPDATE` | 自动更新 | false |
| `UPDATE_INTERVAL` | 更新检查间隔(秒) | 3600 |

### 支持的文件格式

#### 图片格式
- JPG, JPEG, PNG, GIF, WebP

#### 视频格式
- MP4, AVI, MOV, MKV, WebM

#### 音频格式
- MP3, WAV, OGG, M4A, FLAC

#### 文档格式
- PDF, DOC, DOCX, TXT, ZIP, RAR

## 🎯 使用方法

### 基本命令
- `/start` - 开始使用机器人
- `/help` - 显示帮助信息
- `/status` - 显示机器人状态
- `/info` - 显示功能信息

### 管理员命令
- `/admin` - 管理员面板
- `/chat` - 私聊管理
- `/stats` - 统计信息
- `/addadmin` - 添加管理员
- `/removeadmin` - 移除管理员
- `/update` - 检查更新（超级管理员）
- `/script` - 生成安装脚本（超级管理员）

### 发送多媒体
1. 直接发送图片、视频、音频等文件
2. 机器人会自动下载并保存
3. 回复详细的文件信息
4. 提供交互式按钮

### 特殊功能
- **联系人分享**: 发送联系人信息，机器人会显示详细信息
- **位置分享**: 发送位置，机器人会提供地图链接
- **语音消息**: 发送语音，机器人会保存并显示时长信息

## 🔒 安全特性

- 文件大小限制
- 文件类型验证
- 用户权限控制
- 安全的文件命名
- 错误处理和日志记录

## 🌐 部署选项

### 1. Ubuntu一键部署（推荐）

我们提供了完整的Ubuntu部署脚本，支持一键安装所有依赖和服务。脚本支持普通用户（需要sudo权限）和root用户：

#### 快速部署（开发测试）
```bash
# 下载并运行快速部署脚本
wget https://raw.githubusercontent.com/your-repo/your-project/main/quick_deploy.sh
chmod +x quick_deploy.sh
./quick_deploy.sh
```

#### 完整部署（生产环境）
```bash
# 下载并运行完整部署脚本
wget https://raw.githubusercontent.com/your-repo/your-project/main/ubuntu_deploy.sh
chmod +x ubuntu_deploy.sh
./ubuntu_deploy.sh
```

#### 部署测试
```bash
# 部署完成后，运行测试脚本验证
./test_deployment.sh
```

**Ubuntu部署脚本特性：**
- ✅ 自动安装系统依赖（Python、Redis、Nginx等）
- ✅ 创建Python虚拟环境
- ✅ 配置系统服务（systemd）
- ✅ 自动配置防火墙和日志轮转
- ✅ 包含备份和监控脚本
- ✅ 支持可选安装MySQL、MongoDB、Docker

### 2. 本地部署
```bash
# 安装依赖
pip install -r requirements.txt

# 配置环境变量
cp env_example.txt .env
# 编辑 .env 文件

# 运行机器人
python bot.py
```

### 3. Docker部署
```bash
# 使用Docker Compose
docker-compose up -d

# 或使用Dockerfile
docker build -t telegram-bot .
docker run -d --name bot telegram-bot
```

### 4. 云服务器部署
1. 上传代码到服务器
2. 安装Python和依赖
3. 配置环境变量
4. 使用systemd或supervisor管理进程
5. 配置反向代理（Webhook模式）

### 5. 部署脚本对比

| 功能 | 快速部署 | 完整部署 | Docker部署 |
|------|----------|----------|------------|
| 安装速度 | ⚡ 快速 | 🐌 完整 | 🚀 快速 |
| 功能完整性 | 🔧 基础 | 🎯 完整 | 🐳 容器化 |
| 系统集成 | ✅ 基础 | ✅ 完整 | ❌ 独立 |
| 维护便利性 | ⭐ 简单 | ⭐⭐⭐ 完善 | ⭐⭐ 中等 |
| 适用场景 | 开发测试 | 生产环境 | 容器环境 |

## 📊 监控和日志

### 日志级别
- INFO: 一般信息
- WARNING: 警告信息
- ERROR: 错误信息

### 健康检查
Webhook模式下提供 `/health` 端点进行健康检查。

## 🛠️ 开发指南

### 添加新的消息处理器
1. 在 `handlers.py` 中创建新的处理函数
2. 在 `bot.py` 中注册处理器
3. 更新配置和文档

### 自定义文件处理
1. 修改 `utils.py` 中的工具函数
2. 更新 `config.py` 中的配置
3. 调整处理器逻辑

## 🐛 故障排除

### 常见问题

**Q: 机器人没有响应？**
A: 检查BOT_TOKEN是否正确，确认机器人已启动

**Q: 文件下载失败？**
A: 检查网络连接，确认文件大小未超过限制

**Q: Webhook模式无法工作？**
A: 检查WEBHOOK_URL和端口配置，确认服务器可访问

**Q: Ubuntu部署后服务无法启动？**
A: 检查服务状态：`sudo systemctl status telegram-bot`，查看日志：`sudo journalctl -u telegram-bot -f`

**Q: 部署脚本执行失败？**
A: 确保使用普通用户（非root）运行，检查sudo权限，查看错误日志

**Q: Redis连接失败？**
A: 检查Redis服务状态：`sudo systemctl status redis-server`，测试连接：`redis-cli ping`

**Q: Nginx无法访问？**
A: 检查Nginx状态：`sudo systemctl status nginx`，检查防火墙配置：`sudo ufw status`

### 日志查看

#### 应用日志
```bash
# 查看实时日志
tail -f bot.log

# 查看错误日志
grep ERROR bot.log

# 查看系统服务日志
sudo journalctl -u telegram-bot -f
```

#### 系统日志
```bash
# Nginx日志
sudo tail -f /var/log/nginx/error.log

# Redis日志
sudo tail -f /var/log/redis/redis-server.log

# 系统日志
sudo tail -f /var/log/syslog
```

### Ubuntu部署故障排除

#### 1. 服务状态检查
```bash
# 检查所有相关服务
sudo systemctl status telegram-bot redis-server nginx

# 检查端口监听
sudo netstat -tlnp | grep -E ':(80|443|6379|8443)'
```

#### 2. 权限问题修复
```bash
# 修复文件权限
sudo chown -R $(whoami):$(whoami) /home/$(whoami)/telegram-bot/
sudo chmod -R 755 /home/$(whoami)/telegram-bot/
```

#### 3. 重新部署
```bash
# 停止服务
sudo systemctl stop telegram-bot

# 清理并重新部署
sudo rm -rf /home/$(whoami)/telegram-bot/
./ubuntu_deploy.sh
```

#### 4. 运行测试脚本
```bash
# 验证部署
./test_deployment.sh
```

## 📝 更新日志

### v2.1.0
- 🆕 新增Ubuntu一键部署脚本
  - `ubuntu_deploy.sh` - 完整版部署脚本（生产环境）
  - `quick_deploy.sh` - 快速部署脚本（开发测试）
  - `test_deployment.sh` - 部署测试脚本
- 🆕 自动系统配置
  - 自动安装Python、Redis、Nginx等依赖
  - 自动配置防火墙、日志轮转、备份脚本
  - 支持可选安装MySQL、MongoDB、Docker
- 🆕 系统服务集成
  - 创建systemd服务，支持开机自启
  - 创建专用服务用户，提高安全性
  - 集成监控和健康检查

### v2.0.0
- 新增多管理员支持
- 新增私聊选择功能
- 新增管理员回复功能
- 新增数据库支持
- 新增云更新系统
- 新增一键安装脚本生成

### v1.0.0
- 初始版本发布
- 支持多种多媒体类型
- 双向通信功能
- 文件自动下载和保存

## 🤝 贡献

欢迎提交Issue和Pull Request！

## 📄 许可证

MIT License

## 📞 支持

如有问题，请通过以下方式联系：
- 提交GitHub Issue
- 发送邮件至开发者

---

**注意**: 使用前请确保遵守Telegram Bot API的使用条款和当地法律法规。