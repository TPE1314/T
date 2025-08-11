import asyncio
import logging
import os
import aiofiles
from datetime import datetime
from typing import Optional, Union

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application, CommandHandler, MessageHandler, CallbackQueryHandler,
    ContextTypes, filters
)
from telegram.constants import ParseMode

import config
from handlers import (
    handle_start, handle_help, handle_echo, handle_photo, handle_video,
    handle_audio, handle_document, handle_voice, handle_contact,
    handle_location, handle_sticker, handle_animation, handle_contact_callback,
    handle_admin, handle_chat, handle_stats, handle_addadmin, handle_removeadmin,
    handle_reply_message, handle_admin_reply, handle_view_history, 
    handle_start_private, handle_user_stats, handle_update_check,
    handle_perform_update, handle_generate_install_script, handle_script_generation
)

# 配置日志
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

class TelegramBot:
    def __init__(self):
        self.application = Application.builder().token(config.BOT_TOKEN).build()
        self.setup_handlers()

    def setup_handlers(self):
        """设置所有消息处理器"""
        # Command handlers
        self.application.add_handler(CommandHandler("start", handle_start))
        self.application.add_handler(CommandHandler("help", handle_help))
        self.application.add_handler(CommandHandler("status", self.handle_status))
        self.application.add_handler(CommandHandler("info", self.handle_info))
        
        # 管理员命令
        self.application.add_handler(CommandHandler("admin", handle_admin))
        self.application.add_handler(CommandHandler("chat", handle_chat))
        self.application.add_handler(CommandHandler("stats", handle_stats))
        self.application.add_handler(CommandHandler("addadmin", handle_addadmin))
        self.application.add_handler(CommandHandler("removeadmin", handle_removeadmin))
        
        # 新增的管理员功能命令
        self.application.add_handler(CommandHandler("update", handle_update_check))
        self.application.add_handler(CommandHandler("script", handle_generate_install_script))

        # Multimedia message handlers
        self.application.add_handler(MessageHandler(filters.PHOTO, handle_photo))
        self.application.add_handler(MessageHandler(filters.VIDEO, handle_video))
        self.application.add_handler(MessageHandler(filters.AUDIO, handle_audio))
        self.application.add_handler(MessageHandler(filters.Document.ALL, handle_document))
        self.application.add_handler(MessageHandler(filters.VOICE, handle_voice))
        self.application.add_handler(MessageHandler(filters.STICKER, handle_sticker))
        self.application.add_handler(MessageHandler(filters.ANIMATION, handle_animation))

        # Special message handlers
        self.application.add_handler(MessageHandler(filters.CONTACT, handle_contact))
        self.application.add_handler(MessageHandler(filters.LOCATION, handle_location))

        # Callback query handler
        self.application.add_handler(CallbackQueryHandler(handle_contact_callback))

        # Default text message handler
        self.application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_echo))

        # Error handler
        self.application.add_error_handler(self.error_handler)

    async def handle_status(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """处理状态命令"""
        user = update.effective_user
        chat_id = update.effective_chat.id
        
        # 导入管理员管理器
        from admin_manager import admin_manager
        
        status_text = f"🤖 机器人状态\n\n"
        status_text += f"👤 用户ID: {user.id}\n"
        status_text += f"📱 聊天ID: {chat_id}\n"
        status_text += f"⏰ 时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
        status_text += f"💾 存储路径: {config.UPLOAD_FOLDER}\n"
        status_text += f"📁 最大文件大小: {config.MAX_FILE_SIZE // (1024*1024)}MB\n"
        
        # 添加管理员状态信息
        if admin_manager.is_admin(user.id):
            admin_info = admin_manager.get_admin_info(user.id)
            if admin_info:
                status_text += f"\n👨‍💼 管理员状态:\n"
                status_text += f"• 权限: {'超级管理员' if admin_info.is_super_admin else '管理员'}\n"
                status_text += f"• 私聊数量: {len(admin_info.private_chats)}/{admin_info.max_private_chats}\n"
                status_text += f"• 最后活动: {admin_info.last_active[:19]}"
        
        # 添加系统统计信息
        stats = admin_manager.get_admin_stats()
        status_text += f"\n\n📊 系统统计:\n"
        status_text += f"• 总管理员: {stats['total_admins']}\n"
        status_text += f"• 在线管理员: {stats['online_admins']}\n"
        status_text += f"• 总私聊数: {stats['total_private_chats']}\n"
        status_text += f"• 待处理请求: {stats['pending_requests']}"

        await update.message.reply_text(status_text)

    async def handle_info(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """处理信息命令"""
        info_text = "📋 机器人信息\n\n"
        info_text += "🔧 功能特性:\n"
        info_text += "• 支持图片、视频、音频、文档等多媒体\n"
        info_text += "• 支持语音消息和贴纸\n"
        info_text += "• 支持联系人信息和位置分享\n"
        info_text += "• 双向通信，可回复用户消息\n"
        info_text += "• 多管理员支持\n"
        info_text += "• 私聊选择功能\n\n"
        
        info_text += "📱 支持的文件格式:\n"
        info_text += f"• 图片: {', '.join(config.SUPPORTED_PHOTO_FORMATS)}\n"
        info_text += f"• 视频: {', '.join(config.SUPPORTED_VIDEO_FORMATS)}\n"
        info_text += f"• 音频: {', '.join(config.SUPPORTED_AUDIO_FORMATS)}\n"
        info_text += f"• 文档: {', '.join(config.SUPPORTED_DOCUMENT_FORMATS)}\n\n"
        
        info_text += "👥 管理员功能:\n"
        info_text += "• 私聊管理\n"
        info_text += "• 用户请求处理\n"
        info_text += "• 统计信息查看\n"
        info_text += "• 文件管理\n\n"
        
        info_text += "💬 私聊功能:\n"
        if config.ENABLE_PRIVATE_CHAT:
            info_text += f"• 已启用\n"
            info_text += f"• 每个管理员最多 {config.MAX_PRIVATE_CHATS_PER_ADMIN} 个私聊\n"
        else:
            info_text += "• 已禁用\n"
        
        info_text += "\n💡 使用 /help 查看详细帮助"

        await update.message.reply_text(info_text)

    async def error_handler(self, update: object, context: ContextTypes.DEFAULT_TYPE):
        """处理错误"""
        logger.error(f"Exception while handling an update: {context.error}")

        if update and hasattr(update, 'effective_message'):
            await update.effective_message.reply_text(
                "❌ 抱歉，处理您的消息时出现了错误。请稍后重试。"
            )

    async def start_polling(self):
        """开始轮询模式"""
        logger.info("启动机器人轮询模式...")
        await self.application.initialize()
        await self.application.start()
        await self.application.run_polling(allowed_updates=Update.ALL_TYPES)

    async def start_webhook(self):
        """启动Webhook模式"""
        logger.info("启动机器人Webhook模式...")
        await self.application.initialize()
        await self.application.start()
        await self.application.bot.set_webhook(url=config.WEBHOOK_URL)
        await self.application.run_webhook(
            listen="0.0.0.0",
            port=config.WEBHOOK_PORT,
            webhook_url=config.WEBHOOK_URL
        )

async def main():
    """主函数"""
    if not config.BOT_TOKEN:
        logger.error("未设置BOT_TOKEN环境变量")
        return

    bot = TelegramBot()

    # 根据配置选择启动模式
    if config.WEBHOOK_URL:
        await bot.start_webhook()
    else:
        await bot.start_polling()

if __name__ == "__main__":
    asyncio.run(main())