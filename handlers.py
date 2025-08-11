import asyncio
import logging
import os
import aiofiles
from datetime import datetime
from typing import Optional

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from telegram.constants import ParseMode

import config
from utils import (
    get_file_extension, is_supported_file_type, format_file_size,
    generate_filename, ensure_directory_exists, format_duration
)
from admin_manager import admin_manager
from database import db, User, Message, Reply
from update_manager import update_manager

logger = logging.getLogger(__name__)

async def handle_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """处理 /start 命令"""
    user = update.effective_user
    chat_id = update.effective_chat.id
    
    # 检查是否为管理员
    is_admin = admin_manager.is_admin(user.id)
    is_super_admin = admin_manager.is_super_admin(user.id)
    
    # 更新管理员活动状态
    if is_admin:
        admin_manager.update_admin_activity(user.id)
    
    # 添加或更新用户到数据库
    user_info = User(
        user_id=user.id,
        username=user.username or f"user_{user.id}",
        first_name=user.first_name or "",
        last_name=user.last_name or "",
        join_date=datetime.now().isoformat(),
        last_active=datetime.now().isoformat()
    )
    await db.add_user(user_info)
    
    welcome_text = f"👋 欢迎 {user.first_name}！\n\n"
    
    if is_admin:
        if is_super_admin:
            welcome_text += "🔑 您是超级管理员\n"
        else:
            welcome_text += "👨‍💼 您是管理员\n"
        welcome_text += "💡 使用 /admin 查看管理命令\n"
    else:
        welcome_text += "🤖 我是您的智能助手\n"
        if config.ENABLE_PRIVATE_CHAT:
            welcome_text += "💬 需要私聊管理员？使用 /chat 命令\n"
    
    welcome_text += "\n📋 使用 /help 查看所有功能"
    
    # 创建内联键盘
    keyboard = []
    
    if config.ENABLE_PRIVATE_CHAT and not is_admin:
        keyboard.append([InlineKeyboardButton("💬 私聊管理员", callback_data="private_chat")])
    
    if is_admin:
        keyboard.append([InlineKeyboardButton("📊 管理面板", callback_data="admin_panel")])
    
    keyboard.append([InlineKeyboardButton("📖 帮助", callback_data="help")])
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(welcome_text, reply_markup=reply_markup)
    logger.info(f"用户 {user.id} 启动了机器人")

async def handle_help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """处理 /help 命令"""
    user = update.effective_user
    is_admin = admin_manager.is_admin(user.id)
    
    help_text = "📖 机器人帮助\n\n"
    help_text += "🔧 基本命令:\n"
    help_text += "/start - 启动机器人\n"
    help_text += "/help - 显示此帮助\n"
    help_text += "/status - 查看机器人状态\n"
    help_text += "/info - 查看机器人信息\n"
    
    if config.ENABLE_PRIVATE_CHAT:
        help_text += "/chat - 选择管理员私聊\n"
    
    if is_admin:
        help_text += "\n👨‍💼 管理员命令:\n"
        help_text += "/admin - 管理面板\n"
        help_text += "/stats - 查看统计信息\n"
        help_text += "/users - 查看用户列表\n"
        
        if admin_manager.is_super_admin(user.id):
            help_text += "/addadmin - 添加管理员\n"
            help_text += "/removeadmin - 移除管理员\n"
    
    help_text += "\n📱 支持的消息类型:\n"
    help_text += "• 文字消息\n"
    help_text += "• 图片、视频、音频\n"
    help_text += "• 文档、语音、贴纸\n"
    help_text += "• 联系人和位置信息"
    
    await update.message.reply_text(help_text)
    logger.info(f"用户 {user.id} 查看了帮助")

async def handle_admin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """处理 /admin 命令"""
    user = update.effective_user
    
    if not admin_manager.is_admin(user.id):
        await update.message.reply_text("❌ 您没有管理员权限")
        return
    
    admin_info = admin_manager.get_admin_info(user.id)
    if not admin_info:
        await update.message.reply_text("❌ 获取管理员信息失败")
        return
    
    # 更新活动状态
    admin_manager.update_admin_activity(user.id)
    
    admin_text = f"👨‍💼 管理员面板\n\n"
    admin_text += f"🆔 用户ID: {user.id}\n"
    admin_text += f"👤 用户名: {user.username or '无'}\n"
    admin_text += f"📅 加入时间: {admin_info.join_date[:10]}\n"
    admin_text += f"⏰ 最后活动: {admin_info.last_active[:19]}\n"
    admin_text += f"💬 当前私聊: {len(admin_info.private_chats)}/{admin_info.max_private_chats}\n"
    admin_text += f"🔑 权限: {'超级管理员' if admin_info.is_super_admin else '管理员'}"
    
    # 获取待处理的私聊请求
    pending_requests = admin_manager.get_pending_requests(user.id)
    if pending_requests:
        admin_text += f"\n\n⏳ 待处理私聊请求: {len(pending_requests)}"
    
    # 创建管理面板键盘
    keyboard = []
    
    # 私聊管理
    if admin_info.private_chats:
        keyboard.append([InlineKeyboardButton("💬 管理私聊", callback_data="manage_chats")])
    
    if pending_requests:
        keyboard.append([InlineKeyboardButton("⏳ 处理请求", callback_data="handle_requests")])
    
    # 统计信息
    keyboard.append([InlineKeyboardButton("📊 统计信息", callback_data="admin_stats")])
    
    # 超级管理员功能
    if admin_info.is_super_admin:
        keyboard.append([InlineKeyboardButton("👥 管理员管理", callback_data="manage_admins")])
    
    keyboard.append([InlineKeyboardButton("🔙 返回", callback_data="back_to_start")])
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(admin_text, reply_markup=reply_markup)
    logger.info(f"管理员 {user.id} 访问了管理面板")

async def handle_chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """处理 /chat 命令 - 选择管理员私聊"""
    user = update.effective_user
    
    if not config.ENABLE_PRIVATE_CHAT:
        await update.message.reply_text("❌ 私聊功能已禁用")
        return
    
    if admin_manager.is_admin(user.id):
        await update.message.reply_text("❌ 管理员不能使用私聊功能")
        return
    
    # 检查是否已有私聊请求
    if user.id in admin_manager.private_chat_requests:
        request = admin_manager.private_chat_requests[user.id]
        if request.status == "pending":
            await update.message.reply_text("⏳ 您已有待处理的私聊请求，请等待管理员回复")
            return
        elif request.status == "accepted":
            await update.message.reply_text("✅ 您已与管理员建立私聊，请直接发送消息")
            return
    
    # 获取可用的管理员
    available_admins = admin_manager.get_available_admins()
    
    if not available_admins:
        await update.message.reply_text("❌ 当前没有可用的管理员，请稍后再试")
        return
    
    chat_text = "💬 选择管理员私聊\n\n"
    chat_text += "请选择一位管理员进行私聊：\n\n"
    
    # 创建管理员选择键盘
    keyboard = []
    for admin in available_admins:
        status = "🟢 在线" if admin.is_online else "🔴 离线"
        private_chat_count = len(admin.private_chats)
        button_text = f"{admin.first_name} ({status}) - {private_chat_count}/{admin.max_private_chats}"
        keyboard.append([InlineKeyboardButton(button_text, callback_data=f"select_admin_{admin.user_id}")])
    
    keyboard.append([InlineKeyboardButton("❌ 取消", callback_data="cancel_chat")])
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(chat_text, reply_markup=reply_markup)
    logger.info(f"用户 {user.id} 请求选择管理员私聊")

async def handle_stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """处理 /stats 命令 - 显示统计信息"""
    user = update.effective_user
    
    if not admin_manager.is_admin(user.id):
        await update.message.reply_text("❌ 您没有管理员权限")
        return
    
    stats = admin_manager.get_admin_stats()
    
    stats_text = "📊 机器人统计信息\n\n"
    stats_text += f"👥 总管理员数: {stats['total_admins']}\n"
    stats_text += f"🔑 超级管理员数: {stats['super_admins']}\n"
    stats_text += f"🟢 在线管理员数: {stats['online_admins']}\n"
    stats_text += f"💬 总私聊数: {stats['total_private_chats']}\n"
    stats_text += f"⏳ 待处理请求: {stats['pending_requests']}\n"
    stats_text += f"📁 上传目录: {config.UPLOAD_FOLDER}\n"
    stats_text += f"💾 最大文件大小: {config.MAX_FILE_SIZE // (1024*1024)}MB"
    
    await update.message.reply_text(stats_text)
    logger.info(f"管理员 {user.id} 查看了统计信息")

async def handle_addadmin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """处理 /addadmin 命令 - 添加管理员"""
    user = update.effective_user
    
    if not admin_manager.is_super_admin(user.id):
        await update.message.reply_text("❌ 只有超级管理员可以添加管理员")
        return
    
    if not context.args:
        await update.message.reply_text("❌ 请提供用户名或用户ID\n用法: /addadmin <用户名或用户ID>")
        return
    
    target = context.args[0]
    
    # 这里需要实现通过用户名或用户ID添加管理员的逻辑
    # 由于需要用户交互，这里只提供说明
    await update.message.reply_text(
        "📝 添加管理员功能\n\n"
        "请使用以下方式之一：\n"
        "1. 让目标用户先与机器人对话\n"
        "2. 使用 /addadmin_by_username <用户名>\n"
        "3. 使用 /addadmin_by_id <用户ID>"
    )

async def handle_removeadmin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """处理 /removeadmin 命令 - 移除管理员"""
    user = update.effective_user
    
    if not admin_manager.is_super_admin(user.id):
        await update.message.reply_text("❌ 只有超级管理员可以移除管理员")
        return
    
    if not context.args:
        await update.message.reply_text("❌ 请提供管理员ID\n用法: /removeadmin <管理员ID>")
        return
    
    try:
        admin_id = int(context.args[0])
        if admin_manager.remove_admin(admin_id):
            await update.message.reply_text(f"✅ 已成功移除管理员 {admin_id}")
        else:
            await update.message.reply_text(f"❌ 移除管理员 {admin_id} 失败")
    except ValueError:
        await update.message.reply_text("❌ 无效的管理员ID")

# 保留原有的多媒体处理函数
async def handle_echo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """处理文本消息"""
    user = update.effective_user
    chat_id = update.effective_chat.id
    text = update.message.text
    
    logger.info(f"收到来自用户 {user.id} 的文本消息: {text}")
    
    # 记录消息到数据库
    message = Message(
        message_id=update.message.message_id,
        user_id=user.id,
        chat_id=chat_id,
        message_type="text",
        content=text,
        timestamp=datetime.now().isoformat()
    )
    await db.add_message(message)
    
    # 更新用户活动时间
    await db.update_user_activity(user.id)
    
    # 检查是否为私聊
    if chat_id == user.id:  # 私聊
        # 检查用户是否与管理员有私聊
        if user.id in admin_manager.private_chat_requests:
            request = admin_manager.private_chat_requests[user.id]
            if request.status == "accepted":
                # 转发消息给管理员
                admin_id = request.admin_id
                admin_info = admin_manager.get_admin_info(admin_id)
                if admin_info:
                    forward_text = f"💬 来自用户 {user.first_name} (@{user.username or '无用户名'}) 的消息:\n\n{text}"
                    
                    # 创建回复按钮
                    keyboard = [
                        [InlineKeyboardButton("💬 回复", callback_data=f"reply_{update.message.message_id}")],
                        [InlineKeyboardButton("📋 查看历史", callback_data=f"history_{user.id}")]
                    ]
                    reply_markup = InlineKeyboardMarkup(keyboard)
                    
                    try:
                        await context.bot.send_message(admin_id, forward_text, reply_markup=reply_markup)
                        await update.message.reply_text("✅ 消息已发送给管理员")
                    except Exception as e:
                        logger.error(f"转发消息失败: {e}")
                        await update.message.reply_text("❌ 发送消息失败，请稍后重试")
                return
        
        # 如果没有私聊，提供选择管理员的选项
        await handle_chat(update, context)
        return
    
    # 群聊消息处理
    response_text = f"👋 你好 {user.first_name}！\n\n"
    response_text += f"📝 你说: {text}\n\n"
    response_text += "💡 使用 /help 查看所有功能"
    
    await update.message.reply_text(response_text)

async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """处理图片消息"""
    user = update.effective_user
    chat_id = update.effective_chat.id
    photo = update.message.photo[-1]  # 获取最高质量的图片
    
    logger.info(f"收到来自用户 {user.id} 的图片")
    
    # 检查文件大小
    if photo.file_size and photo.file_size > config.MAX_FILE_SIZE:
        await update.message.reply_text(f"❌ 文件过大，最大支持 {config.MAX_FILE_SIZE // (1024*1024)}MB")
        return
    
    try:
        # 下载图片
        file = await context.bot.get_file(photo.file_id)
        file_extension = get_file_extension(file.file_path)
        
        if not is_supported_file_type(file_extension, config.SUPPORTED_PHOTO_FORMATS):
            await update.message.reply_text(f"❌ 不支持的图片格式: {file_extension}")
            return
        
        # 生成文件名
        filename = generate_filename("photo", file_extension)
        file_path = os.path.join(config.UPLOAD_FOLDER, filename)
        
        # 确保目录存在
        ensure_directory_exists(config.UPLOAD_FOLDER)
        
        # 下载文件
        await file.download_to_drive(file_path)
        
        # 获取文件信息
        file_size = format_file_size(photo.file_size) if photo.file_size else "未知"
        
        response_text = f"📸 图片已保存\n\n"
        response_text += f"📁 文件名: {filename}\n"
        response_text += f"💾 文件大小: {file_size}\n"
        response_text += f"📏 尺寸: {photo.width} x {photo.height}\n"
        response_text += f"🔗 文件ID: {photo.file_id}"
        
        # 创建内联键盘
        keyboard = [
            [InlineKeyboardButton("📁 查看文件", callback_data=f"view_file_{filename}")],
            [InlineKeyboardButton("🗑️ 删除文件", callback_data=f"delete_file_{filename}")]
        ]
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(response_text, reply_markup=reply_markup)
        logger.info(f"图片已保存: {file_path}")
        
    except Exception as e:
        logger.error(f"处理图片失败: {e}")
        await update.message.reply_text("❌ 处理图片时出现错误")

async def handle_video(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """处理视频消息"""
    user = update.effective_user
    video = update.message.video
    
    logger.info(f"收到来自用户 {user.id} 的视频")
    
    # 检查文件大小
    if video.file_size and video.file_size > config.MAX_FILE_SIZE:
        await update.message.reply_text(f"❌ 文件过大，最大支持 {config.MAX_FILE_SIZE // (1024*1024)}MB")
        return
    
    try:
        # 下载视频
        file = await context.bot.get_file(video.file_id)
        file_extension = get_file_extension(file.file_path)
        
        if not is_supported_file_type(file_extension, config.SUPPORTED_VIDEO_FORMATS):
            await update.message.reply_text(f"❌ 不支持的视频格式: {file_extension}")
            return
        
        # 生成文件名
        filename = generate_filename("video", file_extension)
        file_path = os.path.join(config.UPLOAD_FOLDER, filename)
        
        # 确保目录存在
        ensure_directory_exists(config.UPLOAD_FOLDER)
        
        # 下载文件
        await file.download_to_drive(file_path)
        
        # 获取文件信息
        file_size = format_file_size(video.file_size) if video.file_size else "未知"
        duration = format_duration(video.duration) if video.duration else "未知"
        
        response_text = f"🎥 视频已保存\n\n"
        response_text += f"📁 文件名: {filename}\n"
        response_text += f"💾 文件大小: {file_size}\n"
        response_text += f"⏱️ 时长: {duration}\n"
        response_text += f"📏 尺寸: {video.width} x {video.height}\n"
        response_text += f"🔗 文件ID: {video.file_id}"
        
        # 创建内联键盘
        keyboard = [
            [InlineKeyboardButton("📁 查看文件", callback_data=f"view_file_{filename}")],
            [InlineKeyboardButton("🗑️ 删除文件", callback_data=f"delete_file_{filename}")]
        ]
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(response_text, reply_markup=reply_markup)
        logger.info(f"视频已保存: {file_path}")
        
    except Exception as e:
        logger.error(f"处理视频失败: {e}")
        await update.message.reply_text("❌ 处理视频时出现错误")

async def handle_audio(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """处理音频消息"""
    user = update.effective_user
    audio = update.message.audio
    
    logger.info(f"收到来自用户 {user.id} 的音频")
    
    # 检查文件大小
    if audio.file_size and audio.file_size > config.MAX_FILE_SIZE:
        await update.message.reply_text(f"❌ 文件过大，最大支持 {config.MAX_FILE_SIZE // (1024*1024)}MB")
        return
    
    try:
        # 下载音频
        file = await context.bot.get_file(audio.file_id)
        file_extension = get_file_extension(file.file_path)
        
        if not is_supported_file_type(file_extension, config.SUPPORTED_AUDIO_FORMATS):
            await update.message.reply_text(f"❌ 不支持的音频格式: {file_extension}")
            return
        
        # 生成文件名
        filename = generate_filename("audio", file_extension)
        file_path = os.path.join(config.UPLOAD_FOLDER, filename)
        
        # 确保目录存在
        ensure_directory_exists(config.UPLOAD_FOLDER)
        
        # 下载文件
        await file.download_to_drive(file_path)
        
        # 获取文件信息
        file_size = format_file_size(audio.file_size) if audio.file_size else "未知"
        duration = format_duration(audio.duration) if audio.duration else "未知"
        title = audio.title or "未知"
        performer = audio.performer or "未知"
        
        response_text = f"🎵 音频已保存\n\n"
        response_text += f"📁 文件名: {filename}\n"
        response_text += f"💾 文件大小: {file_size}\n"
        response_text += f"⏱️ 时长: {duration}\n"
        response_text += f"🎤 演唱者: {performer}\n"
        response_text += f"📝 标题: {title}\n"
        response_text += f"🔗 文件ID: {audio.file_id}"
        
        # 创建内联键盘
        keyboard = [
            [InlineKeyboardButton("📁 查看文件", callback_data=f"view_file_{filename}")],
            [InlineKeyboardButton("🗑️ 删除文件", callback_data=f"delete_file_{filename}")]
        ]
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(response_text, reply_markup=reply_markup)
        logger.info(f"音频已保存: {file_path}")
        
    except Exception as e:
        logger.error(f"处理音频失败: {e}")
        await update.message.reply_text("❌ 处理音频时出现错误")

async def handle_document(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """处理文档消息"""
    user = update.effective_user
    document = update.message.document
    
    logger.info(f"收到来自用户 {user.id} 的文档")
    
    # 检查文件大小
    if document.file_size and document.file_size > config.MAX_FILE_SIZE:
        await update.message.reply_text(f"❌ 文件过大，最大支持 {config.MAX_FILE_SIZE // (1024*1024)}MB")
        return
    
    try:
        # 下载文档
        file = await context.bot.get_file(document.file_id)
        file_extension = get_file_extension(file.file_path)
        
        if not is_supported_file_type(file_extension, config.SUPPORTED_DOCUMENT_FORMATS):
            await update.message.reply_text(f"❌ 不支持的文档格式: {file_extension}")
            return
        
        # 生成文件名
        filename = generate_filename("document", file_extension)
        file_path = os.path.join(config.UPLOAD_FOLDER, filename)
        
        # 确保目录存在
        ensure_directory_exists(config.UPLOAD_FOLDER)
        
        # 下载文件
        await file.download_to_drive(file_path)
        
        # 获取文件信息
        file_size = format_file_size(document.file_size) if document.file_size else "未知"
        mime_type = document.mime_type or "未知"
        
        response_text = f"📄 文档已保存\n\n"
        response_text += f"📁 文件名: {filename}\n"
        response_text += f"💾 文件大小: {file_size}\n"
        response_text += f"📋 MIME类型: {mime_type}\n"
        response_text += f"🔗 文件ID: {document.file_id}"
        
        # 创建内联键盘
        keyboard = [
            [InlineKeyboardButton("📁 查看文件", callback_data=f"view_file_{filename}")],
            [InlineKeyboardButton("🗑️ 删除文件", callback_data=f"delete_file_{filename}")]
        ]
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(response_text, reply_markup=reply_markup)
        logger.info(f"文档已保存: {file_path}")
        
    except Exception as e:
        logger.error(f"处理文档失败: {e}")
        await update.message.reply_text("❌ 处理文档时出现错误")

async def handle_voice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """处理语音消息"""
    user = update.effective_user
    voice = update.message.voice
    
    logger.info(f"收到来自用户 {user.id} 的语音消息")
    
    # 检查文件大小
    if voice.file_size and voice.file_size > config.MAX_FILE_SIZE:
        await update.message.reply_text(f"❌ 文件过大，最大支持 {config.MAX_FILE_SIZE // (1024*1024)}MB")
        return
    
    try:
        # 下载语音
        file = await context.bot.get_file(voice.file_id)
        file_extension = get_file_extension(file.file_path)
        
        # 生成文件名
        filename = generate_filename("voice", file_extension)
        file_path = os.path.join(config.UPLOAD_FOLDER, filename)
        
        # 确保目录存在
        ensure_directory_exists(config.UPLOAD_FOLDER)
        
        # 下载文件
        await file.download_to_drive(file_path)
        
        # 获取文件信息
        file_size = format_file_size(voice.file_size) if voice.file_size else "未知"
        duration = format_duration(voice.duration) if voice.duration else "未知"
        
        response_text = f"🎤 语音消息已保存\n\n"
        response_text += f"📁 文件名: {filename}\n"
        response_text += f"💾 文件大小: {file_size}\n"
        response_text += f"⏱️ 时长: {duration}\n"
        response_text += f"🔗 文件ID: {voice.file_id}"
        
        # 创建内联键盘
        keyboard = [
            [InlineKeyboardButton("📁 查看文件", callback_data=f"view_file_{filename}")],
            [InlineKeyboardButton("🗑️ 删除文件", callback_data=f"delete_file_{filename}")]
        ]
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(response_text, reply_markup=reply_markup)
        logger.info(f"语音消息已保存: {file_path}")
        
    except Exception as e:
        logger.error(f"处理语音消息失败: {e}")
        await update.message.reply_text("❌ 处理语音消息时出现错误")

async def handle_sticker(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """处理贴纸消息"""
    user = update.effective_user
    sticker = update.message.sticker
    
    logger.info(f"收到来自用户 {user.id} 的贴纸")
    
    try:
        # 下载贴纸
        file = await context.bot.get_file(sticker.file_id)
        file_extension = get_file_extension(file.file_path)
        
        # 生成文件名
        filename = generate_filename("sticker", file_extension)
        file_path = os.path.join(config.UPLOAD_FOLDER, filename)
        
        # 确保目录存在
        ensure_directory_exists(config.UPLOAD_FOLDER)
        
        # 下载文件
        await file.download_to_drive(file_path)
        
        # 获取文件信息
        file_size = format_file_size(sticker.file_size) if sticker.file_size else "未知"
        emoji = sticker.emoji or "无"
        set_name = sticker.set_name or "未知"
        
        response_text = f"😀 贴纸已保存\n\n"
        response_text += f"📁 文件名: {filename}\n"
        response_text += f"💾 文件大小: {file_size}\n"
        response_text += f"😊 表情: {emoji}\n"
        response_text += f"📦 贴纸包: {set_name}\n"
        response_text += f"🔗 文件ID: {sticker.file_id}"
        
        # 创建内联键盘
        keyboard = [
            [InlineKeyboardButton("📁 查看文件", callback_data=f"view_file_{filename}")],
            [InlineKeyboardButton("🗑️ 删除文件", callback_data=f"delete_file_{filename}")]
        ]
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(response_text, reply_markup=reply_markup)
        logger.info(f"贴纸已保存: {file_path}")
        
    except Exception as e:
        logger.error(f"处理贴纸失败: {e}")
        await update.message.reply_text("❌ 处理贴纸时出现错误")

async def handle_animation(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """处理动画消息"""
    user = update.effective_user
    animation = update.message.animation
    
    logger.info(f"收到来自用户 {user.id} 的动画")
    
    # 检查文件大小
    if animation.file_size and animation.file_size > config.MAX_FILE_SIZE:
        await update.message.reply_text(f"❌ 文件过大，最大支持 {config.MAX_FILE_SIZE // (1024*1024)}MB")
        return
    
    try:
        # 下载动画
        file = await context.bot.get_file(animation.file_id)
        file_extension = get_file_extension(file.file_path)
        
        # 生成文件名
        filename = generate_filename("animation", file_extension)
        file_path = os.path.join(config.UPLOAD_FOLDER, filename)
        
        # 确保目录存在
        ensure_directory_exists(config.UPLOAD_FOLDER)
        
        # 下载文件
        await file.download_to_drive(file_path)
        
        # 获取文件信息
        file_size = format_file_size(animation.file_size) if animation.file_size else "未知"
        duration = format_duration(animation.duration) if animation.duration else "未知"
        
        response_text = f"🎬 动画已保存\n\n"
        response_text += f"📁 文件名: {filename}\n"
        response_text += f"💾 文件大小: {file_size}\n"
        response_text += f"⏱️ 时长: {duration}\n"
        response_text += f"📏 尺寸: {animation.width} x {animation.height}\n"
        response_text += f"🔗 文件ID: {animation.file_id}"
        
        # 创建内联键盘
        keyboard = [
            [InlineKeyboardButton("📁 查看文件", callback_data=f"view_file_{filename}")],
            [InlineKeyboardButton("🗑️ 删除文件", callback_data=f"delete_file_{filename}")]
        ]
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(response_text, reply_markup=reply_markup)
        logger.info(f"动画已保存: {file_path}")
        
    except Exception as e:
        logger.error(f"处理动画失败: {e}")
        await update.message.reply_text("❌ 处理动画时出现错误")

async def handle_contact(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """处理联系人消息"""
    user = update.effective_user
    contact = update.message.contact
    
    logger.info(f"收到来自用户 {user.id} 的联系人信息")
    
    response_text = f"👤 联系人信息\n\n"
    response_text += f"📱 姓名: {contact.first_name}"
    if contact.last_name:
        response_text += f" {contact.last_name}"
    response_text += f"\n📞 电话: {contact.phone_number}"
    if contact.user_id:
        response_text += f"\n🆔 用户ID: {contact.user_id}"
    
    # 创建内联键盘
    keyboard = [
        [InlineKeyboardButton("📞 拨打电话", callback_data=f"call_{contact.phone_number}")],
        [InlineKeyboardButton("💬 发送消息", callback_data=f"message_{contact.user_id or 'unknown'}")]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(response_text, reply_markup=reply_markup)

async def handle_location(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """处理位置消息"""
    user = update.effective_user
    location = update.message.location
    
    logger.info(f"收到来自用户 {user.id} 的位置信息")
    
    response_text = f"📍 位置信息\n\n"
    response_text += f"🌍 纬度: {location.latitude}\n"
    response_text += f"🌍 经度: {location.longitude}"
    
    # 创建内联键盘
    keyboard = [
        [InlineKeyboardButton("🗺️ 查看地图", callback_data=f"map_{location.latitude}_{location.longitude}")],
        [InlineKeyboardButton("📍 导航", callback_data=f"navigate_{location.latitude}_{location.longitude}")]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(response_text, reply_markup=reply_markup)

async def handle_contact_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """处理联系人相关的回调查询"""
    query = update.callback_query
    await query.answer()
    
    data = query.data
    
    if data.startswith("call_"):
        phone = data.split("_", 1)[1]
        await query.edit_message_text(f"📞 正在拨打: {phone}")
    
    elif data.startswith("message_"):
        user_id = data.split("_", 1)[1]
        if user_id != "unknown":
            await query.edit_message_text(f"💬 正在向用户 {user_id} 发送消息")
        else:
            await query.edit_message_text("❌ 无法获取用户ID")
    
    elif data.startswith("map_"):
        coords = data.split("_", 1)[1]
        lat, lon = coords.split("_")
        map_url = f"https://maps.google.com/?q={lat},{lon}"
        await query.edit_message_text(f"🗺️ 地图链接: {map_url}")
    
    elif data.startswith("navigate_"):
        coords = data.split("_", 1)[1]
        lat, lon = coords.split("_")
        nav_url = f"https://maps.google.com/directions?daddr={lat},{lon}"
        await query.edit_message_text(f"📍 导航链接: {nav_url}")
    
    elif data == "private_chat":
        await handle_chat(update, context)
    
    elif data == "admin_panel":
        await handle_admin(update, context)
    
    elif data == "help":
        await handle_help(update, context)
    
    elif data == "back_to_start":
        await handle_start(update, context)
    
    elif data.startswith("select_admin_"):
        admin_id = int(data.split("_", 2)[2])
        user = query.from_user
        
        success, message = admin_manager.request_private_chat(user, admin_id)
        await query.edit_message_text(message)
        
        if success:
            # 通知管理员
            admin_info = admin_manager.get_admin_info(admin_id)
            if admin_info:
                notification = f"🔔 新的私聊请求\n\n"
                notification += f"👤 用户: {user.first_name} (@{user.username or '无用户名'})\n"
                notification += f"🆔 用户ID: {user.id}\n"
                notification += f"⏰ 时间: {datetime.now().strftime('%H:%M:%S')}"
                
                keyboard = [
                    [InlineKeyboardButton("✅ 接受", callback_data=f"accept_chat_{user.id}")],
                    [InlineKeyboardButton("❌ 拒绝", callback_data=f"reject_chat_{user.id}")]
                ]
                reply_markup = InlineKeyboardMarkup(keyboard)
                
                try:
                    await context.bot.send_message(admin_id, notification, reply_markup=reply_markup)
                except Exception as e:
                    logger.error(f"通知管理员失败: {e}")
    
    elif data.startswith("accept_chat_"):
        user_id = int(data.split("_", 2)[2])
        admin_id = query.from_user.id
        
        if admin_manager.accept_private_chat(admin_id, user_id):
            await query.edit_message_text("✅ 已接受私聊请求")
            
            # 通知用户
            try:
                await context.bot.send_message(user_id, "✅ 您的私聊请求已被接受！现在可以直接发送消息。")
            except Exception as e:
                logger.error(f"通知用户失败: {e}")
        else:
            await query.edit_message_text("❌ 接受私聊请求失败")
    
    elif data.startswith("reject_chat_"):
        user_id = int(data.split("_", 2)[2])
        admin_id = query.from_user.id
        
        if admin_manager.reject_private_chat(admin_id, user_id):
            await query.edit_message_text("❌ 已拒绝私聊请求")
            
            # 通知用户
            try:
                await context.bot.send_message(user_id, "❌ 您的私聊请求已被拒绝。")
            except Exception as e:
                logger.error(f"通知用户失败: {e}")
        else:
            await query.edit_message_text("❌ 拒绝私聊请求失败")
    
    elif data == "manage_chats":
        await handle_manage_chats(update, context)
    
    elif data == "handle_requests":
        await handle_pending_requests(update, context)
    
    elif data == "admin_stats":
        await handle_stats(update, context)
    
    elif data == "manage_admins":
        await handle_manage_admins(update, context)
    
    elif data == "cancel_chat":
        await query.edit_message_text("❌ 已取消选择管理员")
    
    # 新增的回调处理功能
    elif data.startswith("reply_"):
        await handle_reply_message(update, context)
    
    elif data.startswith("history_"):
        await handle_view_history(update, context)
    
    elif data.startswith("start_private_"):
        await handle_start_private(update, context)
    
    elif data.startswith("user_stats_"):
        await handle_user_stats(update, context)
    
    elif data == "perform_update":
        await handle_perform_update(update, context)
    
    elif data == "update_details":
        await query.edit_message_text("📋 更新详情功能开发中...")
    
    elif data.startswith("script_"):
        await handle_script_generation(update, context)
    
    # 文件管理回调
    elif data.startswith("view_file_"):
        filename = data.split("_", 2)[2]
        file_path = os.path.join(config.UPLOAD_FOLDER, filename)
        
        if os.path.exists(file_path):
            try:
                await context.bot.send_document(
                    chat_id=query.from_user.id,
                    document=open(file_path, 'rb'),
                    caption=f"📁 文件: {filename}"
                )
                await query.answer("✅ 文件已发送")
            except Exception as e:
                logger.error(f"发送文件失败: {e}")
                await query.answer("❌ 发送文件失败")
        else:
            await query.answer("❌ 文件不存在")
    
    elif data.startswith("delete_file_"):
        filename = data.split("_", 2)[2]
        file_path = os.path.join(config.UPLOAD_FOLDER, filename)
        
        if os.path.exists(file_path):
            try:
                os.remove(file_path)
                await query.edit_message_text(f"🗑️ 文件 {filename} 已删除")
                await query.answer("✅ 文件已删除")
            except Exception as e:
                logger.error(f"删除文件失败: {e}")
                await query.answer("❌ 删除文件失败")
        else:
            await query.answer("❌ 文件不存在")
    
    # 聊天管理回调
    elif data.startswith("view_chat_"):
        user_id = int(data.split("_", 2)[2])
        await query.edit_message_text(f"💬 查看与用户 {user_id} 的聊天记录...")
        # 这里可以添加查看聊天记录的逻辑
    
    elif data.startswith("view_request_"):
        user_id = int(data.split("_", 2)[2])
        await query.edit_message_text(f"📋 查看用户 {user_id} 的请求详情...")
        # 这里可以添加查看请求详情的逻辑
    
    elif data.startswith("manage_admin_"):
        admin_id = int(data.split("_", 2)[2])
        await query.edit_message_text(f"⚙️ 管理管理员 {admin_id}...")
        # 这里可以添加管理员的逻辑

async def handle_manage_chats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """处理管理私聊"""
    user = update.effective_user
    admin_info = admin_manager.get_admin_info(user.id)
    
    if not admin_info or not admin_info.private_chats:
        await update.callback_query.edit_message_text("❌ 您当前没有私聊")
        return
    
    chat_text = "💬 管理私聊\n\n"
    chat_text += f"当前私聊数量: {len(admin_info.private_chats)}/{admin_info.max_private_chats}\n\n"
    
    keyboard = []
    for chat_id in admin_info.private_chats:
        try:
            chat_member = await context.bot.get_chat(chat_id)
            chat_name = chat_member.first_name or f"用户{chat_id}"
            keyboard.append([InlineKeyboardButton(f"👤 {chat_name}", callback_data=f"view_chat_{chat_id}")])
        except:
            keyboard.append([InlineKeyboardButton(f"👤 用户{chat_id}", callback_data=f"view_chat_{chat_id}")])
    
    keyboard.append([InlineKeyboardButton("🔙 返回", callback_data="admin_panel")])
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.callback_query.edit_message_text(chat_text, reply_markup=reply_markup)

async def handle_pending_requests(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """处理待处理的私聊请求"""
    user = update.effective_user
    pending_requests = admin_manager.get_pending_requests(user.id)
    
    if not pending_requests:
        await update.callback_query.edit_message_text("✅ 没有待处理的私聊请求")
        return
    
    request_text = f"⏳ 待处理的私聊请求\n\n"
    request_text += f"数量: {len(pending_requests)}\n\n"
    
    keyboard = []
    for request in pending_requests:
        try:
            chat_member = await context.bot.get_chat(request.user_id)
            chat_name = chat_member.first_name or f"用户{request.user_id}"
            keyboard.append([InlineKeyboardButton(f"👤 {chat_name}", callback_data=f"view_request_{request.user_id}")])
        except:
            keyboard.append([InlineKeyboardButton(f"👤 用户{request.user_id}", callback_data=f"view_request_{request.user_id}")])
    
    keyboard.append([InlineKeyboardButton("🔙 返回", callback_data="admin_panel")])
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.callback_query.edit_message_text(request_text, reply_markup=reply_markup)

async def handle_manage_admins(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """处理管理员管理"""
    user = update.effective_user
    
    if not admin_manager.is_super_admin(user.id):
        await update.callback_query.edit_message_text("❌ 您没有超级管理员权限")
        return
    
    admins = list(admin_manager.admin_sessions.values())
    admin_text = f"👥 管理员管理\n\n"
    admin_text += f"总数量: {len(admins)}\n\n"
    
    keyboard = []
    for admin in admins:
        if admin.user_id != user.id:  # 不能移除自己
            status = "🟢 在线" if admin.is_online else "🔴 离线"
            role = "🔑 超级管理员" if admin.is_super_admin else "👨‍💼 管理员"
            button_text = f"{admin.first_name} ({status}) - {role}"
            keyboard.append([InlineKeyboardButton(button_text, callback_data=f"manage_admin_{admin.user_id}")])
    
    keyboard.append([InlineKeyboardButton("🔙 返回", callback_data="admin_panel")])
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.callback_query.edit_message_text(admin_text, reply_markup=reply_markup)

async def handle_reply_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """处理管理员回复消息"""
    user = update.effective_user
    query = update.callback_query
    
    if not admin_manager.is_admin(user.id):
        await query.answer("❌ 您没有权限执行此操作")
        return
    
    # 解析消息ID
    try:
        message_id = int(query.data.split('_')[1])
    except (IndexError, ValueError):
        await query.answer("❌ 无效的消息ID")
        return
    
    # 获取消息信息
    message, replies = await db.get_message_with_replies(message_id)
    if not message:
        await query.answer("❌ 消息不存在")
        return
    
    # 获取用户信息
    user_info = await db.get_user(message.user_id)
    if not user_info:
        await query.answer("❌ 用户信息不存在")
        return
    
    # 创建回复界面
    reply_text = f"💬 回复用户 {user_info.first_name} (@{user_info.username})\n\n"
    reply_text += f"📝 原消息: {message.content}\n"
    reply_text += f"⏰ 时间: {message.timestamp}\n\n"
    
    if replies:
        reply_text += "📋 回复历史:\n"
        for i, reply in enumerate(replies, 1):
            reply_text += f"{i}. {reply.content} ({reply.timestamp})\n"
    
    reply_text += "\n💡 请直接发送回复内容"
    
    # 存储回复状态
    context.user_data['replying_to'] = message_id
    context.user_data['reply_user_id'] = message.user_id
    
    await query.edit_message_text(reply_text)
    await query.answer("请发送回复内容")

async def handle_admin_reply(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """处理管理员的回复内容"""
    user = update.effective_user
    text = update.message.text
    
    if not admin_manager.is_admin(user.id):
        return
    
    # 检查是否在回复状态
    if 'replying_to' not in context.user_data:
        return
    
    message_id = context.user_data['replying_to']
    reply_user_id = context.user_data['reply_user_id']
    
    # 创建回复记录
    reply = Reply(
        reply_id=0,  # 数据库自动生成
        original_message_id=message_id,
        admin_id=user.id,
        content=text,
        message_type="text",
        timestamp=datetime.now().isoformat()
    )
    
    # 保存回复到数据库
    if await db.add_reply(reply):
        # 发送回复给用户
        try:
            reply_text = f"💬 管理员回复:\n\n{text}"
            await context.bot.send_message(reply_user_id, reply_text)
            
            # 通知管理员
            await update.message.reply_text("✅ 回复已发送给用户")
            
            # 清除回复状态
            del context.user_data['replying_to']
            del context.user_data['reply_user_id']
            
        except Exception as e:
            logger.error(f"发送回复失败: {e}")
            await update.message.reply_text("❌ 发送回复失败，请稍后重试")
    else:
        await update.message.reply_text("❌ 保存回复失败")

async def handle_view_history(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """查看用户聊天历史"""
    user = update.effective_user
    query = update.callback_query
    
    if not admin_manager.is_admin(user.id):
        await query.answer("❌ 您没有权限执行此操作")
        return
    
    # 解析用户ID
    try:
        user_id = int(query.data.split('_')[1])
    except (IndexError, ValueError):
        await query.answer("❌ 无效的用户ID")
        return
    
    # 获取用户信息
    user_info = await db.get_user(user_id)
    if not user_info:
        await query.answer("❌ 用户信息不存在")
        return
    
    # 获取用户消息历史
    messages = await db.get_user_messages(user_id, limit=20)
    
    if not messages:
        await query.answer("该用户暂无消息记录")
        return
    
    # 创建历史记录显示
    history_text = f"📋 用户 {user_info.first_name} (@{user_info.username}) 的聊天历史\n\n"
    
    for i, msg in enumerate(messages[:10], 1):  # 只显示最近10条
        timestamp = msg.timestamp.split('T')[0] if 'T' in msg.timestamp else msg.timestamp
        status = "✅ 已回复" if msg.is_replied else "⏳ 待回复"
        history_text += f"{i}. [{status}] {msg.content[:50]}{'...' if len(msg.content) > 50 else ''} ({timestamp})\n"
    
    if len(messages) > 10:
        history_text += f"\n... 还有 {len(messages) - 10} 条消息"
    
    # 创建操作按钮
    keyboard = [
        [InlineKeyboardButton("💬 开始私聊", callback_data=f"start_private_{user_id}")],
        [InlineKeyboardButton("📊 用户统计", callback_data=f"user_stats_{user_id}")],
        [InlineKeyboardButton("🔙 返回", callback_data="admin_panel")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(history_text, reply_markup=reply_markup)
    await query.answer("已显示聊天历史")

async def handle_start_private(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """开始与用户私聊"""
    user = update.effective_user
    query = update.callback_query
    
    if not admin_manager.is_admin(user.id):
        await query.answer("❌ 您没有权限执行此操作")
        return
    
    # 解析用户ID
    try:
        user_id = int(query.data.split('_')[2])
    except (IndexError, ValueError):
        await query.answer("❌ 无效的用户ID")
        return
    
    # 检查管理员是否已达到私聊上限
    admin_info = admin_manager.get_admin_info(user.id)
    if len(admin_info.private_chats) >= admin_info.max_private_chats:
        await query.answer("❌ 您已达到私聊上限")
        return
    
    # 创建私聊请求
    success, message = admin_manager.request_private_chat(
        User(user_id, "", "", "", "", ""), user.id
    )
    
    if success:
        # 直接接受私聊
        admin_manager.accept_private_chat(user.id, user_id)
        
        # 通知用户
        try:
            await context.bot.send_message(
                user_id, 
                f"💬 管理员 {user.first_name} 已开始与您私聊\n\n请直接发送消息"
            )
        except Exception as e:
            logger.error(f"通知用户私聊开始失败: {e}")
        
        await query.answer("✅ 私聊已开始")
        await query.edit_message_text("💬 私聊已开始，请等待用户消息")
    else:
        await query.answer(f"❌ {message}")

async def handle_user_stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """查看用户统计信息"""
    user = update.effective_user
    query = update.callback_query
    
    if not admin_manager.is_admin(user.id):
        await query.answer("❌ 您没有权限执行此操作")
        return
    
    # 解析用户ID
    try:
        user_id = int(query.data.split('_')[2])
    except (IndexError, ValueError):
        await query.answer("❌ 无效的用户ID")
        return
    
    # 获取用户信息
    user_info = await db.get_user(user_id)
    if not user_info:
        await query.answer("❌ 用户信息不存在")
        return
    
    # 获取用户消息统计
    messages = await db.get_user_messages(user_id, limit=1000)
    total_messages = len(messages)
    replied_messages = len([m for m in messages if m.is_replied])
    reply_rate = (replied_messages / total_messages * 100) if total_messages > 0 else 0
    
    # 计算活跃度
    if user_info.last_active:
        last_active = user_info.last_active.split('T')[0] if 'T' in user_info.last_active else user_info.last_active
    else:
        last_active = "未知"
    
    stats_text = f"📊 用户 {user_info.first_name} (@{user_info.username}) 统计信息\n\n"
    stats_text += f"🆔 用户ID: {user_id}\n"
    stats_text += f"📅 加入时间: {user_info.join_date.split('T')[0] if 'T' in user_info.join_date else user_info.join_date}\n"
    stats_text += f"🕐 最后活跃: {last_active}\n"
    stats_text += f"📝 总消息数: {total_messages}\n"
    stats_text += f"✅ 已回复: {replied_messages}\n"
    stats_text += f"📈 回复率: {reply_rate:.1f}%\n"
    stats_text += f"🚫 是否被封禁: {'是' if user_info.is_blocked else '否'}\n"
    
    if user_info.is_blocked:
        stats_text += f"🚫 封禁原因: {user_info.block_reason}\n"
    
    # 创建操作按钮
    keyboard = [
        [InlineKeyboardButton("💬 开始私聊", callback_data=f"start_private_{user_id}")],
        [InlineKeyboardButton("📋 查看历史", callback_data=f"history_{user_id}")],
        [InlineKeyboardButton("🔙 返回", callback_data="admin_panel")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(stats_text, reply_markup=reply_markup)
    await query.answer("已显示用户统计")

async def handle_update_check(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """检查更新"""
    user = update.effective_user
    
    if not admin_manager.is_super_admin(user.id):
        await update.message.reply_text("❌ 只有超级管理员可以检查更新")
        return
    
    await update.message.reply_text("🔄 正在检查更新...")
    
    try:
        update_result = await update_manager.check_for_updates()
        
        if update_result.has_update:
            update_text = f"🆕 发现新版本!\n\n"
            update_text += f"📱 当前版本: {update_result.current_version}\n"
            update_text += f"🆙 最新版本: {update_result.latest_version}\n"
            update_text += f"📝 更新说明: {update_result.description}\n"
            update_text += f"🔗 下载地址: {update_result.download_url}\n"
            update_text += f"📅 发布日期: {update_result.release_date}\n"
            update_text += f"⚠️ 强制更新: {'是' if update_result.is_forced else '否'}\n"
            
            if update_result.changelog:
                update_text += f"\n📋 更新日志:\n{update_result.changelog}"
            
            # 创建更新按钮
            keyboard = [
                [InlineKeyboardButton("🔄 立即更新", callback_data="perform_update")],
                [InlineKeyboardButton("📋 更新详情", callback_data="update_details")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await update.message.reply_text(update_text, reply_markup=reply_markup)
        else:
            await update.message.reply_text("✅ 当前已是最新版本")
            
    except Exception as e:
        logger.error(f"检查更新失败: {e}")
        await update.message.reply_text("❌ 检查更新失败")

async def handle_perform_update(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """执行更新"""
    user = update.effective_user
    query = update.callback_query
    
    if not admin_manager.is_super_admin(user.id):
        await query.answer("❌ 只有超级管理员可以执行更新")
        return
    
    await query.answer("🔄 开始执行更新...")
    
    try:
        # 获取最新更新信息
        update_result = await update_manager.check_for_updates()
        if not update_result.has_update:
            await query.edit_message_text("❌ 没有可用的更新")
            return
        
        # 执行更新
        success = await update_manager.perform_update(update_result)
        
        if success:
            await query.edit_message_text("✅ 更新完成！机器人将在重启后生效")
        else:
            await query.edit_message_text("❌ 更新失败，请检查日志")
            
    except Exception as e:
        logger.error(f"执行更新失败: {e}")
        await query.edit_message_text("❌ 执行更新失败")

async def handle_generate_install_script(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """生成一键安装脚本"""
    user = update.effective_user
    
    if not admin_manager.is_super_admin(user.id):
        await update.message.reply_text("❌ 只有超级管理员可以生成安装脚本")
        return
    
    # 创建脚本选择按钮
    keyboard = [
        [InlineKeyboardButton("🐧 Linux安装脚本", callback_data="script_linux")],
        [InlineKeyboardButton("🪟 Windows安装脚本", callback_data="script_windows")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        "🔧 选择要生成的安装脚本类型:",
        reply_markup=reply_markup
    )

async def handle_script_generation(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """处理脚本生成请求"""
    user = update.effective_user
    query = update.callback_query
    
    if not admin_manager.is_super_admin(user.id):
        await query.answer("❌ 只有超级管理员可以生成安装脚本")
        return
    
    platform = query.data.split('_')[1]
    
    try:
        # 生成脚本
        script_content = update_manager.get_update_script(platform)
        
        # 保存脚本文件
        filename = f"install_telegram_bot_{platform}.{'sh' if platform == 'linux' else 'bat'}"
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(script_content)
        
        # 发送脚本文件
        await context.bot.send_document(
            chat_id=user.id,
            document=open(filename, 'rb'),
            caption=f"🔧 {platform.title()} 一键安装脚本已生成\n\n使用方法:\n1. 下载脚本文件\n2. 设置执行权限 (Linux: chmod +x)\n3. 运行脚本"
        )
        
        # 清理临时文件
        os.remove(filename)
        
        await query.answer("✅ 安装脚本已生成")
        
    except Exception as e:
        logger.error(f"生成安装脚本失败: {e}")
        await query.answer("❌ 生成脚本失败")