import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# Telegram Bot配置
BOT_TOKEN = os.getenv('BOT_TOKEN')
WEBHOOK_URL = os.getenv('WEBHOOK_URL', '')
WEBHOOK_PORT = int(os.getenv('WEBHOOK_PORT', '8443'))

# 文件存储配置
UPLOAD_FOLDER = os.getenv('UPLOAD_FOLDER', './uploads')
MAX_FILE_SIZE = int(os.getenv('MAX_FILE_SIZE', '50')) * 1024 * 1024  # 50MB

# 管理员配置
ADMIN_IDS = [int(id.strip()) for id in os.getenv('ADMIN_IDS', '').split(',') if id.strip().isdigit()]
SUPER_ADMIN_ID = int(os.getenv('SUPER_ADMIN_ID', '0')) if os.getenv('SUPER_ADMIN_ID', '').isdigit() else None

# 私聊配置
ENABLE_PRIVATE_CHAT = os.getenv('ENABLE_PRIVATE_CHAT', 'true').lower() == 'true'
MAX_PRIVATE_CHATS_PER_ADMIN = int(os.getenv('MAX_PRIVATE_CHATS_PER_ADMIN', '10'))

# 支持的文件类型
SUPPORTED_PHOTO_FORMATS = ['.jpg', '.jpeg', '.png', '.gif', '.webp']
SUPPORTED_VIDEO_FORMATS = ['.mp4', '.avi', '.mov', '.mkv', '.webm']
SUPPORTED_AUDIO_FORMATS = ['.mp3', '.wav', '.ogg', '.m4a', '.flac']
SUPPORTED_DOCUMENT_FORMATS = ['.pdf', '.doc', '.docx', '.txt', '.zip', '.rar']

# 数据库配置
DATABASE_URL = os.getenv('DATABASE_URL', 'data/bot.db')

# 更新配置
UPDATE_CHECK_URL = os.getenv('UPDATE_CHECK_URL', '')
AUTO_UPDATE = os.getenv('AUTO_UPDATE', 'false').lower() == 'true'
UPDATE_INTERVAL = int(os.getenv('UPDATE_INTERVAL', '3600'))

# 确保上传目录存在
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# 默认管理员（如果环境变量未设置）
if not ADMIN_IDS:
    ADMIN_IDS = [123456789]  # 替换为你的Telegram用户ID