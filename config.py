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

# 支持的文件类型
SUPPORTED_PHOTO_FORMATS = ['.jpg', '.jpeg', '.png', '.gif', '.webp']
SUPPORTED_VIDEO_FORMATS = ['.mp4', '.avi', '.mov', '.mkv', '.webm']
SUPPORTED_AUDIO_FORMATS = ['.mp3', '.wav', '.ogg', '.m4a', '.flac']
SUPPORTED_DOCUMENT_FORMATS = ['.pdf', '.doc', '.docx', '.txt', '.zip', '.rar']

# 确保上传目录存在
os.makedirs(UPLOAD_FOLDER, exist_ok=True)