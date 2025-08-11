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

## 🚀 快速开始

### 1. 获取Bot Token
1. 在Telegram中搜索 `@BotFather`
2. 发送 `/newbot` 命令
3. 按提示设置机器人名称和用户名
4. 复制获得的Bot Token

### 2. 安装依赖
```bash
pip install -r requirements.txt
```

### 3. 配置环境变量
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

### 4. 运行机器人

#### 轮询模式（推荐用于开发测试）
```bash
python bot.py
```

#### Webhook模式（推荐用于生产环境）
```bash
python webhook_server.py
```

## 📁 项目结构

```
telegram-bot/
├── bot.py              # 主机器人文件
├── handlers.py         # 消息处理器
├── config.py           # 配置文件
├── utils.py            # 工具函数
├── webhook_server.py   # Webhook服务器
├── requirements.txt    # Python依赖
├── env_example.txt     # 环境变量示例
├── README.md          # 项目说明
└── uploads/           # 文件上传目录
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

### 本地部署
```bash
# 安装依赖
pip install -r requirements.txt

# 配置环境变量
cp env_example.txt .env
# 编辑 .env 文件

# 运行机器人
python bot.py
```

### Docker部署
```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
CMD ["python", "bot.py"]
```

### 云服务器部署
1. 上传代码到服务器
2. 安装Python和依赖
3. 配置环境变量
4. 使用systemd或supervisor管理进程
5. 配置反向代理（Webhook模式）

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

### 日志查看
```bash
# 查看实时日志
tail -f bot.log

# 查看错误日志
grep ERROR bot.log
```

## 📝 更新日志

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