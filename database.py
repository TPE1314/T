import sqlite3
import json
import logging
from datetime import datetime
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass, asdict
import aiosqlite

logger = logging.getLogger(__name__)

@dataclass
class User:
    """用户信息"""
    user_id: int
    username: str
    first_name: str
    last_name: str
    join_date: str
    last_active: str
    is_blocked: bool = False
    block_reason: str = ""

@dataclass
class Message:
    """消息记录"""
    message_id: int
    user_id: int
    chat_id: int
    message_type: str  # text, photo, video, audio, document, etc.
    content: str
    file_id: str = ""
    file_path: str = ""
    timestamp: str = ""
    is_replied: bool = False
    reply_message_id: int = 0

@dataclass
class Reply:
    """回复记录"""
    reply_id: int
    original_message_id: int
    admin_id: int
    content: str
    message_type: str = "text"
    file_id: str = ""
    file_path: str = ""
    timestamp: str = ""
    is_read: bool = False

@dataclass
class UpdateInfo:
    """更新信息"""
    version: str
    description: str
    download_url: str
    release_date: str
    is_forced: bool = False
    changelog: str = ""

class Database:
    """数据库管理器"""
    
    def __init__(self, db_path: str = "data/bot.db"):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """初始化数据库"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # 创建用户表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    user_id INTEGER PRIMARY KEY,
                    username TEXT,
                    first_name TEXT,
                    last_name TEXT,
                    join_date TEXT,
                    last_active TEXT,
                    is_blocked INTEGER DEFAULT 0,
                    block_reason TEXT DEFAULT ''
                )
            ''')
            
            # 创建消息表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS messages (
                    message_id INTEGER PRIMARY KEY,
                    user_id INTEGER,
                    chat_id INTEGER,
                    message_type TEXT,
                    content TEXT,
                    file_id TEXT DEFAULT '',
                    file_path TEXT DEFAULT '',
                    timestamp TEXT,
                    is_replied INTEGER DEFAULT 0,
                    reply_message_id INTEGER DEFAULT 0,
                    FOREIGN KEY (user_id) REFERENCES users (user_id)
                )
            ''')
            
            # 创建回复表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS replies (
                    reply_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    original_message_id INTEGER,
                    admin_id INTEGER,
                    content TEXT,
                    message_type TEXT DEFAULT 'text',
                    file_id TEXT DEFAULT '',
                    file_path TEXT DEFAULT '',
                    timestamp TEXT,
                    is_read INTEGER DEFAULT 0,
                    FOREIGN KEY (original_message_id) REFERENCES messages (message_id)
                )
            ''')
            
            # 创建更新表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS updates (
                    version TEXT PRIMARY KEY,
                    description TEXT,
                    download_url TEXT,
                    release_date TEXT,
                    is_forced INTEGER DEFAULT 0,
                    changelog TEXT DEFAULT ''
                )
            ''')
            
            # 创建索引
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_messages_user_id ON messages(user_id)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_messages_chat_id ON messages(chat_id)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_replies_message_id ON replies(original_message_id)')
            
            conn.commit()
            conn.close()
            logger.info("数据库初始化完成")
            
        except Exception as e:
            logger.error(f"数据库初始化失败: {e}")
    
    async def add_user(self, user: User) -> bool:
        """添加用户"""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                await db.execute('''
                    INSERT OR REPLACE INTO users 
                    (user_id, username, first_name, last_name, join_date, last_active)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (user.user_id, user.username, user.first_name, 
                      user.last_name, user.join_date, user.last_active))
                await db.commit()
                return True
        except Exception as e:
            logger.error(f"添加用户失败: {e}")
            return False
    
    async def update_user_activity(self, user_id: int):
        """更新用户活动时间"""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                await db.execute('''
                    UPDATE users SET last_active = ? WHERE user_id = ?
                ''', (datetime.now().isoformat(), user_id))
                await db.commit()
        except Exception as e:
            logger.error(f"更新用户活动失败: {e}")
    
    async def get_user(self, user_id: int) -> Optional[User]:
        """获取用户信息"""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                async with db.execute('''
                    SELECT * FROM users WHERE user_id = ?
                ''', (user_id,)) as cursor:
                    row = await cursor.fetchone()
                    if row:
                        return User(*row)
                    return None
        except Exception as e:
            logger.error(f"获取用户失败: {e}")
            return None
    
    async def add_message(self, message: Message) -> bool:
        """添加消息"""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                await db.execute('''
                    INSERT INTO messages 
                    (message_id, user_id, chat_id, message_type, content, 
                     file_id, file_path, timestamp)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ''', (message.message_id, message.user_id, message.chat_id,
                      message.message_type, message.content, message.file_id,
                      message.file_path, message.timestamp))
                await db.commit()
                return True
        except Exception as e:
            logger.error(f"添加消息失败: {e}")
            return False
    
    async def get_user_messages(self, user_id: int, limit: int = 50) -> List[Message]:
        """获取用户消息历史"""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                async with db.execute('''
                    SELECT * FROM messages 
                    WHERE user_id = ? 
                    ORDER BY timestamp DESC 
                    LIMIT ?
                ''', (user_id, limit)) as cursor:
                    rows = await cursor.fetchall()
                    return [Message(*row) for row in rows]
        except Exception as e:
            logger.error(f"获取用户消息失败: {e}")
            return []
    
    async def add_reply(self, reply: Reply) -> bool:
        """添加回复"""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                # 添加回复
                await db.execute('''
                    INSERT INTO replies 
                    (original_message_id, admin_id, content, message_type, 
                     file_id, file_path, timestamp)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (reply.original_message_id, reply.admin_id, reply.content,
                      reply.message_type, reply.file_id, reply.file_path, reply.timestamp))
                
                # 更新消息状态
                await db.execute('''
                    UPDATE messages 
                    SET is_replied = 1, reply_message_id = last_insert_rowid()
                    WHERE message_id = ?
                ''', (reply.original_message_id,))
                
                await db.commit()
                return True
        except Exception as e:
            logger.error(f"添加回复失败: {e}")
            return False
    
    async def get_unreplied_messages(self) -> List[Message]:
        """获取未回复的消息"""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                async with db.execute('''
                    SELECT m.* FROM messages m
                    LEFT JOIN replies r ON m.message_id = r.original_message_id
                    WHERE m.is_replied = 0 AND r.reply_id IS NULL
                    ORDER BY m.timestamp ASC
                ''') as cursor:
                    rows = await cursor.fetchall()
                    return [Message(*row) for row in rows]
        except Exception as e:
            logger.error(f"获取未回复消息失败: {e}")
            return []
    
    async def get_message_with_replies(self, message_id: int) -> Tuple[Optional[Message], List[Reply]]:
        """获取消息及其回复"""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                # 获取消息
                async with db.execute('''
                    SELECT * FROM messages WHERE message_id = ?
                ''', (message_id,)) as cursor:
                    row = await cursor.fetchone()
                    message = Message(*row) if row else None
                
                # 获取回复
                async with db.execute('''
                    SELECT * FROM replies WHERE original_message_id = ?
                    ORDER BY timestamp ASC
                ''', (message_id,)) as cursor:
                    rows = await cursor.fetchall()
                    replies = [Reply(*row) for row in rows]
                
                return message, replies
        except Exception as e:
            logger.error(f"获取消息及回复失败: {e}")
            return None, []
    
    async def add_update(self, update_info: UpdateInfo) -> bool:
        """添加更新信息"""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                await db.execute('''
                    INSERT OR REPLACE INTO updates 
                    (version, description, download_url, release_date, is_forced, changelog)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (update_info.version, update_info.description, update_info.download_url,
                      update_info.release_date, update_info.is_forced, update_info.changelog))
                await db.commit()
                return True
        except Exception as e:
            logger.error(f"添加更新信息失败: {e}")
            return False
    
    async def get_latest_update(self) -> Optional[UpdateInfo]:
        """获取最新更新信息"""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                async with db.execute('''
                    SELECT * FROM updates 
                    ORDER BY release_date DESC 
                    LIMIT 1
                ''') as cursor:
                    row = await cursor.fetchone()
                    return UpdateInfo(*row) if row else None
        except Exception as e:
            logger.error(f"获取最新更新失败: {e}")
            return None
    
    async def get_stats(self) -> Dict:
        """获取统计信息"""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                stats = {}
                
                # 用户统计
                async with db.execute('SELECT COUNT(*) FROM users') as cursor:
                    row = await cursor.fetchone()
                    stats['total_users'] = row[0] if row else 0
                
                # 消息统计
                async with db.execute('SELECT COUNT(*) FROM messages') as cursor:
                    row = await cursor.fetchone()
                    stats['total_messages'] = row[0] if row else 0
                
                # 回复统计
                async with db.execute('SELECT COUNT(*) FROM replies') as cursor:
                    row = await cursor.fetchone()
                    stats['total_replies'] = row[0] if row else 0
                
                # 未回复消息
                async with db.execute('SELECT COUNT(*) FROM messages WHERE is_replied = 0') as cursor:
                    row = await cursor.fetchone()
                    stats['unreplied_messages'] = row[0] if row else 0
                
                return stats
        except Exception as e:
            logger.error(f"获取统计信息失败: {e}")
            return {}

# 全局数据库实例
db = Database()