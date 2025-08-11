import json
import os
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict
from telegram import User, Update
from telegram.ext import ContextTypes

import config

logger = logging.getLogger(__name__)

@dataclass
class AdminInfo:
    """管理员信息"""
    user_id: int
    username: str
    first_name: str
    last_name: str
    is_super_admin: bool
    join_date: str
    last_active: str
    private_chats: List[int]  # 当前私聊的用户ID列表
    max_private_chats: int
    is_online: bool

@dataclass
class PrivateChatRequest:
    """私聊请求"""
    user_id: int
    username: str
    first_name: str
    admin_id: int
    request_time: str
    status: str  # pending, accepted, rejected, expired
    chat_id: Optional[int] = None

class AdminManager:
    """管理员管理器"""
    
    def __init__(self):
        self.admins_file = "data/admins.json"
        self.private_chats_file = "data/private_chats.json"
        self.admin_sessions: Dict[int, AdminInfo] = {}
        self.private_chat_requests: Dict[int, PrivateChatRequest] = {}
        
        # 确保数据目录存在
        os.makedirs("data", exist_ok=True)
        
        # 加载管理员数据
        self.load_admins()
        self.load_private_chats()
        
        # 初始化默认管理员
        self.initialize_default_admins()
    
    def initialize_default_admins(self):
        """初始化默认管理员"""
        if not self.admin_sessions:
            # 创建超级管理员
            if config.SUPER_ADMIN_ID:
                super_admin = AdminInfo(
                    user_id=config.SUPER_ADMIN_ID,
                    username="super_admin",
                    first_name="超级管理员",
                    last_name="",
                    is_super_admin=True,
                    join_date=datetime.now().isoformat(),
                    last_active=datetime.now().isoformat(),
                    private_chats=[],
                    max_private_chats=config.MAX_PRIVATE_CHATS_PER_ADMIN,
                    is_online=False
                )
                self.admin_sessions[config.SUPER_ADMIN_ID] = super_admin
            
            # 创建其他管理员
            for admin_id in config.ADMIN_IDS:
                if admin_id not in self.admin_sessions:
                    admin = AdminInfo(
                        user_id=admin_id,
                        username=f"admin_{admin_id}",
                        first_name=f"管理员{admin_id}",
                        last_name="",
                        is_super_admin=False,
                        join_date=datetime.now().isoformat(),
                        last_active=datetime.now().isoformat(),
                        private_chats=[],
                        max_private_chats=config.MAX_PRIVATE_CHATS_PER_ADMIN,
                        is_online=False
                    )
                    self.admin_sessions[admin_id] = admin
            
            self.save_admins()
    
    def load_admins(self):
        """加载管理员数据"""
        try:
            if os.path.exists(self.admins_file):
                with open(self.admins_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    for admin_data in data.values():
                        admin = AdminInfo(**admin_data)
                        self.admin_sessions[admin.user_id] = admin
                logger.info(f"已加载 {len(self.admin_sessions)} 个管理员")
        except Exception as e:
            logger.error(f"加载管理员数据失败: {e}")
    
    def save_admins(self):
        """保存管理员数据"""
        try:
            data = {str(admin_id): asdict(admin) for admin_id, admin in self.admin_sessions.items()}
            with open(self.admins_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"保存管理员数据失败: {e}")
    
    def load_private_chats(self):
        """加载私聊数据"""
        try:
            if os.path.exists(self.private_chats_file):
                with open(self.private_chats_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    for chat_data in data.values():
                        chat = PrivateChatRequest(**chat_data)
                        self.private_chat_requests[chat.user_id] = chat
        except Exception as e:
            logger.error(f"加载私聊数据失败: {e}")
    
    def save_private_chats(self):
        """保存私聊数据"""
        try:
            data = {str(chat.user_id): asdict(chat) for chat in self.private_chat_requests.values()}
            with open(self.private_chats_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"保存私聊数据失败: {e}")
    
    def is_admin(self, user_id: int) -> bool:
        """检查用户是否为管理员"""
        return user_id in self.admin_sessions
    
    def is_super_admin(self, user_id: int) -> bool:
        """检查用户是否为超级管理员"""
        admin = self.admin_sessions.get(user_id)
        return admin.is_super_admin if admin else False
    
    def get_admin_info(self, user_id: int) -> Optional[AdminInfo]:
        """获取管理员信息"""
        return self.admin_sessions.get(user_id)
    
    def add_admin(self, user: User, super_admin: bool = False) -> bool:
        """添加管理员"""
        if user.id in self.admin_sessions:
            return False
        
        admin = AdminInfo(
            user_id=user.id,
            username=user.username or f"user_{user.id}",
            first_name=user.first_name or "",
            last_name=user.last_name or "",
            is_super_admin=super_admin,
            join_date=datetime.now().isoformat(),
            last_active=datetime.now().isoformat(),
            private_chats=[],
            max_private_chats=config.MAX_PRIVATE_CHATS_PER_ADMIN,
            is_online=False
        )
        
        self.admin_sessions[user.id] = admin
        self.save_admins()
        logger.info(f"已添加管理员: {user.id} ({user.first_name})")
        return True
    
    def remove_admin(self, admin_id: int) -> bool:
        """移除管理员"""
        if admin_id not in self.admin_sessions:
            return False
        
        # 超级管理员不能移除自己
        if self.admin_sessions[admin_id].is_super_admin:
            return False
        
        # 清理私聊
        admin = self.admin_sessions[admin_id]
        for chat_id in admin.private_chats:
            if chat_id in self.private_chat_requests:
                del self.private_chat_requests[chat_id]
        
        del self.admin_sessions[admin_id]
        self.save_admins()
        self.save_private_chats()
        logger.info(f"已移除管理员: {admin_id}")
        return True
    
    def update_admin_activity(self, admin_id: int):
        """更新管理员活动时间"""
        if admin_id in self.admin_sessions:
            self.admin_sessions[admin_id].last_active = datetime.now().isoformat()
            self.admin_sessions[admin_id].is_online = True
            self.save_admins()
    
    def get_available_admins(self) -> List[AdminInfo]:
        """获取可用的管理员列表"""
        available = []
        for admin in self.admin_sessions.values():
            if len(admin.private_chats) < admin.max_private_chats:
                available.append(admin)
        return available
    
    def get_admin_by_username(self, username: str) -> Optional[AdminInfo]:
        """根据用户名获取管理员"""
        for admin in self.admin_sessions.values():
            if admin.username == username:
                return admin
        return None
    
    def request_private_chat(self, user: User, admin_id: int) -> Tuple[bool, str]:
        """请求私聊"""
        if not config.ENABLE_PRIVATE_CHAT:
            return False, "私聊功能已禁用"
        
        if user.id in self.private_chat_requests:
            return False, "您已有待处理的私聊请求"
        
        admin = self.admin_sessions.get(admin_id)
        if not admin:
            return False, "指定的管理员不存在"
        
        if len(admin.private_chats) >= admin.max_private_chats:
            return False, "该管理员当前私聊数量已达上限"
        
        # 创建私聊请求
        request = PrivateChatRequest(
            user_id=user.id,
            username=user.username or f"user_{user.id}",
            first_name=user.first_name or "",
            admin_id=admin_id,
            request_time=datetime.now().isoformat(),
            status="pending"
        )
        
        self.private_chat_requests[user.id] = request
        self.save_private_chats()
        
        logger.info(f"用户 {user.id} 请求与管理员 {admin_id} 私聊")
        return True, "私聊请求已发送，请等待管理员回复"
    
    def accept_private_chat(self, admin_id: int, user_id: int) -> bool:
        """接受私聊请求"""
        if user_id not in self.private_chat_requests:
            return False
        
        request = self.private_chat_requests[user_id]
        if request.admin_id != admin_id:
            return False
        
        if request.status != "pending":
            return False
        
        # 更新请求状态
        request.status = "accepted"
        request.chat_id = user_id
        
        # 添加到管理员的私聊列表
        admin = self.admin_sessions.get(admin_id)
        if admin and user_id not in admin.private_chats:
            admin.private_chats.append(user_id)
        
        self.save_private_chats()
        self.save_admins()
        
        logger.info(f"管理员 {admin_id} 接受了用户 {user_id} 的私聊请求")
        return True
    
    def reject_private_chat(self, admin_id: int, user_id: int) -> bool:
        """拒绝私聊请求"""
        if user_id not in self.private_chat_requests:
            return False
        
        request = self.private_chat_requests[user_id]
        if request.admin_id != admin_id:
            return False
        
        request.status = "rejected"
        self.save_private_chats()
        
        logger.info(f"管理员 {admin_id} 拒绝了用户 {user_id} 的私聊请求")
        return True
    
    def end_private_chat(self, admin_id: int, user_id: int) -> bool:
        """结束私聊"""
        admin = self.admin_sessions.get(admin_id)
        if not admin or user_id not in admin.private_chats:
            return False
        
        # 从管理员私聊列表中移除
        admin.private_chats.remove(user_id)
        
        # 清理私聊请求
        if user_id in self.private_chat_requests:
            del self.private_chat_requests[user_id]
        
        self.save_admins()
        self.save_private_chats()
        
        logger.info(f"管理员 {admin_id} 结束了与用户 {user_id} 的私聊")
        return True
    
    def get_pending_requests(self, admin_id: int) -> List[PrivateChatRequest]:
        """获取待处理的私聊请求"""
        pending = []
        for request in self.private_chat_requests.values():
            if request.admin_id == admin_id and request.status == "pending":
                pending.append(request)
        return pending
    
    def cleanup_expired_requests(self, expire_hours: int = 24):
        """清理过期的私聊请求"""
        current_time = datetime.now()
        expired_users = []
        
        for user_id, request in self.private_chat_requests.items():
            if request.status == "pending":
                request_time = datetime.fromisoformat(request.request_time)
                if current_time - request_time > timedelta(hours=expire_hours):
                    expired_users.append(user_id)
        
        for user_id in expired_users:
            del self.private_chat_requests[user_id]
        
        if expired_users:
            self.save_private_chats()
            logger.info(f"已清理 {len(expired_users)} 个过期的私聊请求")
    
    def get_admin_stats(self) -> Dict:
        """获取管理员统计信息"""
        stats = {
            "total_admins": len(self.admin_sessions),
            "super_admins": len([a for a in self.admin_sessions.values() if a.is_super_admin]),
            "online_admins": len([a for a in self.admin_sessions.values() if a.is_online]),
            "total_private_chats": sum(len(a.private_chats) for a in self.admin_sessions.values()),
            "pending_requests": len([r for r in self.private_chat_requests.values() if r.status == "pending"])
        }
        return stats

# 全局管理员管理器实例
admin_manager = AdminManager()