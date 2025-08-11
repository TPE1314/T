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

logger = logging.getLogger(__name__)

async def handle_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """处理开始命令"""
    user = update.effective_user
    welcome_text = f"👋 欢迎 {user.first_name}!\n\n"
    welcome_text += "🤖 我是一个支持多媒体的Telegram机器人\n\n"
    welcome_text += "📱 我可以处理以下类型的消息:\n"
    welcome_text += "• 图片、视频、音频\n"
    welcome_text += "• 文档、语音消息\n"
    welcome_text += "• 贴纸、动画\n"
    welcome_text += "• 联系人、位置信息\n\n"
    welcome_text += "💡 使用 /help 查看详细帮助\n"
    welcome_text += "📊 使用 /status 查看状态\n"
    welcome_text += "ℹ️ 使用 /info 查看功能信息"
    
    # 创建内联键盘
    keyboard = [
        [InlineKeyboardButton("📖 帮助", callback_data="help")],
        [InlineKeyboardButton("📊 状态", callback_data="status")],
        [InlineKeyboardButton("ℹ️ 信息", callback_data="info")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(welcome_text, reply_markup=reply_markup)

async def handle_help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """处理帮助命令"""
    help_text = "📖 机器人帮助\n\n"
    help_text += "🔧 可用命令:\n"
    help_text += "/start - 开始使用机器人\n"
    help_text += "/help - 显示此帮助信息\n"
    help_text += "/status - 显示机器人状态\n"
    help_text += "/info - 显示功能信息\n\n"
    help_text += "📱 支持的消息类型:\n"
    help_text += "• 文本消息 - 机器人会回复确认\n"
    help_text += "• 图片 - 自动下载并保存\n"
    help_text += "• 视频 - 支持多种视频格式\n"
    help_text += "• 音频 - 音乐和语音文件\n"
    help_text += "• 文档 - 各种文档格式\n"
    help_text += "• 语音消息 - 语音录制\n"
    help_text += "• 贴纸 - 表情贴纸\n"
    help_text += "• 动画 - GIF动画\n"
    help_text += "• 联系人 - 联系人信息\n"
    help_text += "• 位置 - 地理位置\n\n"
    help_text += "💡 直接发送任何类型的消息即可开始使用!"
    
    await update.message.reply_text(help_text)

async def handle_echo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """处理文本消息"""
    user = update.effective_user
    text = update.message.text
    
    # 记录用户消息
    logger.info(f"收到来自用户 {user.id} 的文本消息: {text}")
    
    # 回复确认消息
    reply_text = f"✅ 收到您的消息: {text}\n\n"
    reply_text += f"👤 用户: {user.first_name}\n"
    reply_text += f"🆔 用户ID: {user.id}\n"
    reply_text += f"⏰ 时间: {datetime.now().strftime('%H:%M:%S')}"
    
    await update.message.reply_text(reply_text)

async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """处理图片消息"""
    user = update.effective_user
    photo = update.message.photo[-1]  # 获取最高质量的图片
    
    logger.info(f"收到来自用户 {user.id} 的图片")
    
    try:
        # 下载图片
        file = await context.bot.get_file(photo.file_id)
        file_path = os.path.join(config.UPLOAD_FOLDER, f"photo_{user.id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg")
        
        await file.download_to_drive(file_path)
        
        # 获取图片信息
        file_size = os.path.getsize(file_path) / 1024  # KB
        
        reply_text = f"📸 图片已保存!\n\n"
        reply_text += f"👤 用户: {user.first_name}\n"
        reply_text += f"📁 文件名: {os.path.basename(file_path)}\n"
        reply_text += f"💾 文件大小: {file_size:.1f} KB\n"
        reply_text += f"📏 尺寸: {photo.width} x {photo.height}\n"
        reply_text += f"⏰ 时间: {datetime.now().strftime('%H:%M:%S')}"
        
        await update.message.reply_text(reply_text)
        
    except Exception as e:
        logger.error(f"处理图片时出错: {e}")
        await update.message.reply_text("❌ 处理图片时出错，请稍后重试")

async def handle_video(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """处理视频消息"""
    user = update.effective_user
    video = update.message.video
    
    logger.info(f"收到来自用户 {user.id} 的视频")
    
    try:
        # 下载视频
        file = await context.bot.get_file(video.file_id)
        file_path = os.path.join(config.UPLOAD_FOLDER, f"video_{user.id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.mp4")
        
        await file.download_to_drive(file_path)
        
        # 获取视频信息
        file_size = os.path.getsize(file_path) / (1024 * 1024)  # MB
        
        reply_text = f"🎥 视频已保存!\n\n"
        reply_text += f"👤 用户: {user.first_name}\n"
        reply_text += f"📁 文件名: {os.path.basename(file_path)}\n"
        reply_text += f"💾 文件大小: {file_size:.1f} MB\n"
        reply_text += f"📏 尺寸: {video.width} x {video.height}\n"
        reply_text += f"⏱️ 时长: {video.duration} 秒\n"
        reply_text += f"⏰ 时间: {datetime.now().strftime('%H:%M:%S')}"
        
        await update.message.reply_text(reply_text)
        
    except Exception as e:
        logger.error(f"处理视频时出错: {e}")
        await update.message.reply_text("❌ 处理视频时出错，请稍后重试")

async def handle_audio(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """处理音频消息"""
    user = update.effective_user
    audio = update.message.audio
    
    logger.info(f"收到来自用户 {user.id} 的音频")
    
    try:
        # 下载音频
        file = await context.bot.get_file(audio.file_id)
        file_path = os.path.join(config.UPLOAD_FOLDER, f"audio_{user.id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.mp3")
        
        await file.download_to_drive(file_path)
        
        # 获取音频信息
        file_size = os.path.getsize(file_path) / 1024  # KB
        
        reply_text = f"🎵 音频已保存!\n\n"
        reply_text += f"👤 用户: {user.first_name}\n"
        reply_text += f"📁 文件名: {os.path.basename(file_path)}\n"
        reply_text += f"💾 文件大小: {file_size:.1f} KB\n"
        reply_text += f"⏱️ 时长: {audio.duration} 秒\n"
        reply_text += f"🎤 表演者: {audio.performer or '未知'}\n"
        reply_text += f"📝 标题: {audio.title or '未知'}\n"
        reply_text += f"⏰ 时间: {datetime.now().strftime('%H:%M:%S')}"
        
        await update.message.reply_text(reply_text)
        
    except Exception as e:
        logger.error(f"处理音频时出错: {e}")
        await update.message.reply_text("❌ 处理音频时出错，请稍后重试")

async def handle_document(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """处理文档消息"""
    user = update.effective_user
    document = update.message.document
    
    logger.info(f"收到来自用户 {user.id} 的文档: {document.file_name}")
    
    try:
        # 下载文档
        file = await context.bot.get_file(document.file_id)
        file_path = os.path.join(config.UPLOAD_FOLDER, f"doc_{user.id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{document.file_name}")
        
        await file.download_to_drive(file_path)
        
        # 获取文档信息
        file_size = os.path.getsize(file_path) / 1024  # KB
        
        reply_text = f"📄 文档已保存!\n\n"
        reply_text += f"👤 用户: {user.first_name}\n"
        reply_text += f"📁 文件名: {os.path.basename(file_path)}\n"
        reply_text += f"💾 文件大小: {file_size:.1f} KB\n"
        reply_text += f"📋 MIME类型: {document.mime_type or '未知'}\n"
        reply_text += f"⏰ 时间: {datetime.now().strftime('%H:%M:%S')}"
        
        await update.message.reply_text(reply_text)
        
    except Exception as e:
        logger.error(f"处理文档时出错: {e}")
        await update.message.reply_text("❌ 处理文档时出错，请稍后重试")

async def handle_voice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """处理语音消息"""
    user = update.effective_user
    voice = update.message.voice
    
    logger.info(f"收到来自用户 {user.id} 的语音消息")
    
    try:
        # 下载语音
        file = await context.bot.get_file(voice.file_id)
        file_path = os.path.join(config.UPLOAD_FOLDER, f"voice_{user.id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.ogg")
        
        await file.download_to_drive(file_path)
        
        # 获取语音信息
        file_size = os.path.getsize(file_path) / 1024  # KB
        
        reply_text = f"🎤 语音消息已保存!\n\n"
        reply_text += f"👤 用户: {user.first_name}\n"
        reply_text += f"📁 文件名: {os.path.basename(file_path)}\n"
        reply_text += f"💾 文件大小: {file_size:.1f} KB\n"
        reply_text += f"⏱️ 时长: {voice.duration} 秒\n"
        reply_text += f"⏰ 时间: {datetime.now().strftime('%H:%M:%S')}"
        
        await update.message.reply_text(reply_text)
        
    except Exception as e:
        logger.error(f"处理语音消息时出错: {e}")
        await update.message.reply_text("❌ 处理语音消息时出错，请稍后重试")

async def handle_sticker(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """处理贴纸消息"""
    user = update.effective_user
    sticker = update.message.sticker
    
    logger.info(f"收到来自用户 {user.id} 的贴纸")
    
    try:
        # 下载贴纸
        file = await context.bot.get_file(sticker.file_id)
        file_path = os.path.join(config.UPLOAD_FOLDER, f"sticker_{user.id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.webp")
        
        await file.download_to_drive(file_path)
        
        reply_text = f"😀 贴纸已保存!\n\n"
        reply_text += f"👤 用户: {user.first_name}\n"
        reply_text += f"📁 文件名: {os.path.basename(file_path)}\n"
        reply_text += f"📏 尺寸: {sticker.width} x {sticker.height}\n"
        reply_text += f"🏷️ 表情: {sticker.emoji or '无'}\n"
        reply_text += f"📦 贴纸集: {sticker.set_name or '未知'}\n"
        reply_text += f"⏰ 时间: {datetime.now().strftime('%H:%M:%S')}"
        
        await update.message.reply_text(reply_text)
        
    except Exception as e:
        logger.error(f"处理贴纸时出错: {e}")
        await update.message.reply_text("❌ 处理贴纸时出错，请稍后重试")

async def handle_animation(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """处理动画消息"""
    user = update.effective_user
    animation = update.message.animation
    
    logger.info(f"收到来自用户 {user.id} 的动画")
    
    try:
        # 下载动画
        file = await context.bot.get_file(animation.file_id)
        file_path = os.path.join(config.UPLOAD_FOLDER, f"animation_{user.id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.gif")
        
        await file.download_to_drive(file_path)
        
        # 获取动画信息
        file_size = os.path.getsize(file_path) / 1024  # KB
        
        reply_text = f"🎬 动画已保存!\n\n"
        reply_text += f"👤 用户: {user.first_name}\n"
        reply_text += f"📁 文件名: {os.path.basename(file_path)}\n"
        reply_text += f"💾 文件大小: {file_size:.1f} KB\n"
        reply_text += f"📏 尺寸: {animation.width} x {animation.height}\n"
        reply_text += f"⏱️ 时长: {animation.duration} 秒\n"
        reply_text += f"⏰ 时间: {datetime.now().strftime('%H:%M:%S')}"
        
        await update.message.reply_text(reply_text)
        
    except Exception as e:
        logger.error(f"处理动画时出错: {e}")
        await update.message.reply_text("❌ 处理动画时出错，请稍后重试")

async def handle_contact(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """处理联系人消息"""
    user = update.effective_user
    contact = update.message.contact
    
    logger.info(f"收到来自用户 {user.id} 的联系人信息")
    
    reply_text = f"👤 联系人信息已接收!\n\n"
    reply_text += f"📱 发送者: {user.first_name}\n"
    reply_text += f"👨‍💼 联系人姓名: {contact.first_name}"
    
    if contact.last_name:
        reply_text += f" {contact.last_name}"
    
    reply_text += f"\n📞 电话号码: {contact.phone_number}"
    
    if contact.user_id:
        reply_text += f"\n🆔 用户ID: {contact.user_id}"
    
    reply_text += f"\n⏰ 时间: {datetime.now().strftime('%H:%M:%S')}"
    
    # 创建内联键盘
    keyboard = [
        [InlineKeyboardButton("📞 拨打电话", callback_data=f"call_{contact.phone_number}")],
        [InlineKeyboardButton("💬 发送消息", callback_data=f"message_{contact.phone_number}")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(reply_text, reply_markup=reply_markup)

async def handle_location(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """处理位置消息"""
    user = update.effective_user
    location = update.message.location
    
    logger.info(f"收到来自用户 {user.id} 的位置信息")
    
    reply_text = f"📍 位置信息已接收!\n\n"
    reply_text += f"👤 发送者: {user.first_name}\n"
    reply_text += f"🌍 纬度: {location.latitude:.6f}\n"
    reply_text += f"🌍 经度: {location.longitude:.6f}\n"
    
    if location.live_period:
        reply_text += f"⏱️ 实时位置有效期: {location.live_period} 秒\n"
    
    if location.heading:
        reply_text += f"🧭 方向: {location.heading}°\n"
    
    if location.horizontal_accuracy:
        reply_text += f"🎯 水平精度: {location.horizontal_accuracy} 米\n"
    
    reply_text += f"⏰ 时间: {datetime.now().strftime('%H:%M:%S')}"
    
    # 创建内联键盘
    keyboard = [
        [InlineKeyboardButton("🗺️ 查看地图", callback_data=f"map_{location.latitude}_{location.longitude}")],
        [InlineKeyboardButton("📍 获取地址", callback_data=f"address_{location.latitude}_{location.longitude}")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(reply_text, reply_markup=reply_markup)

async def handle_contact_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """处理联系人和位置的回调查询"""
    query = update.callback_query
    await query.answer()
    
    data = query.data
    
    if data.startswith("call_"):
        phone = data.split("_", 1)[1]
        await query.edit_message_text(f"📞 正在拨打: {phone}")
        
    elif data.startswith("message_"):
        phone = data.split("_", 1)[1]
        await query.edit_message_text(f"💬 准备发送消息到: {phone}")
        
    elif data.startswith("map_"):
        coords = data.split("_", 1)[1]
        lat, lon = coords.split("_")
        map_url = f"https://www.google.com/maps?q={lat},{lon}"
        await query.edit_message_text(f"🗺️ 地图链接: {map_url}")
        
    elif data.startswith("address_"):
        coords = data.split("_", 1)[1]
        await query.edit_message_text("📍 正在获取地址信息...")
        
    elif data in ["help", "status", "info"]:
        if data == "help":
            await handle_help(update, context)
        elif data == "status":
            # 这里可以添加状态处理逻辑
            await query.edit_message_text("📊 状态信息功能开发中...")
        elif data == "info":
            # 这里可以添加信息处理逻辑
            await query.edit_message_text("ℹ️ 功能信息功能开发中...")