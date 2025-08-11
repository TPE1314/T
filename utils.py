import os
import hashlib
import mimetypes
from datetime import datetime
from typing import Optional, Tuple
import config

def get_file_extension(filename: str) -> str:
    """获取文件扩展名"""
    return os.path.splitext(filename)[1].lower()

def is_supported_file_type(filename: str) -> Tuple[bool, str]:
    """检查文件类型是否支持"""
    ext = get_file_extension(filename)
    
    if ext in config.SUPPORTED_PHOTO_FORMATS:
        return True, "photo"
    elif ext in config.SUPPORTED_VIDEO_FORMATS:
        return True, "video"
    elif ext in config.SUPPORTED_AUDIO_FORMATS:
        return True, "audio"
    elif ext in config.SUPPORTED_DOCUMENT_FORMATS:
        return True, "document"
    else:
        return False, "unknown"

def get_file_size_mb(file_path: str) -> float:
    """获取文件大小（MB）"""
    try:
        size_bytes = os.path.getsize(file_path)
        return size_bytes / (1024 * 1024)
    except OSError:
        return 0.0

def format_file_size(size_bytes: int) -> str:
    """格式化文件大小显示"""
    if size_bytes < 1024:
        return f"{size_bytes} B"
    elif size_bytes < 1024 * 1024:
        return f"{size_bytes / 1024:.1f} KB"
    elif size_bytes < 1024 * 1024 * 1024:
        return f"{size_bytes / (1024 * 1024):.1f} MB"
    else:
        return f"{size_bytes / (1024 * 1024 * 1024):.1f} GB"

def generate_filename(user_id: int, file_type: str, original_name: str = "") -> str:
    """生成唯一的文件名"""
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    user_hash = hashlib.md5(str(user_id).encode()).hexdigest()[:8]
    
    if original_name:
        ext = get_file_extension(original_name)
        base_name = os.path.splitext(original_name)[0]
        # 清理文件名中的特殊字符
        base_name = "".join(c for c in base_name if c.isalnum() or c in (' ', '-', '_')).rstrip()
        return f"{file_type}_{user_hash}_{timestamp}_{base_name}{ext}"
    else:
        return f"{file_type}_{user_hash}_{timestamp}"

def ensure_directory_exists(directory: str) -> None:
    """确保目录存在，如果不存在则创建"""
    os.makedirs(directory, exist_ok=True)

def get_mime_type(file_path: str) -> Optional[str]:
    """获取文件的MIME类型"""
    return mimetypes.guess_type(file_path)[0]

def is_file_too_large(file_size: int) -> bool:
    """检查文件是否超过最大限制"""
    return file_size > config.MAX_FILE_SIZE

def cleanup_old_files(directory: str, max_age_hours: int = 24) -> int:
    """清理指定目录中的旧文件"""
    cleaned_count = 0
    current_time = datetime.now()
    
    try:
        for filename in os.listdir(directory):
            file_path = os.path.join(directory, filename)
            if os.path.isfile(file_path):
                file_time = datetime.fromtimestamp(os.path.getmtime(file_path))
                age_hours = (current_time - file_time).total_seconds() / 3600
                
                if age_hours > max_age_hours:
                    os.remove(file_path)
                    cleaned_count += 1
    except Exception as e:
        print(f"清理文件时出错: {e}")
    
    return cleaned_count

def get_directory_size(directory: str) -> int:
    """获取目录的总大小（字节）"""
    total_size = 0
    try:
        for dirpath, dirnames, filenames in os.walk(directory):
            for filename in filenames:
                file_path = os.path.join(dirpath, filename)
                if os.path.isfile(file_path):
                    total_size += os.path.getsize(file_path)
    except Exception as e:
        print(f"计算目录大小时出错: {e}")
    
    return total_size

def format_duration(seconds: int) -> str:
    """格式化时长显示"""
    if seconds < 60:
        return f"{seconds}秒"
    elif seconds < 3600:
        minutes = seconds // 60
        remaining_seconds = seconds % 60
        return f"{minutes}分{remaining_seconds}秒"
    else:
        hours = seconds // 3600
        remaining_minutes = (seconds % 3600) // 60
        remaining_seconds = seconds % 60
        return f"{hours}时{remaining_minutes}分{remaining_seconds}秒"