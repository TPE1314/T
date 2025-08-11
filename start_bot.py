#!/usr/bin/env python3
"""
Telegram Bot 启动脚本
支持轮询和Webhook两种模式
"""

import os
import sys
import asyncio
import argparse
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

def check_environment():
    """检查环境配置"""
    bot_token = os.getenv('BOT_TOKEN')
    if not bot_token:
        print("❌ 错误: 未设置BOT_TOKEN环境变量")
        print("请复制 env_example.txt 为 .env 并填写正确的配置")
        return False
    
    print("✅ 环境配置检查通过")
    return True

def check_dependencies():
    """检查依赖包"""
    try:
        import telegram
        import aiohttp
        print("✅ 依赖包检查通过")
        return True
    except ImportError as e:
        print(f"❌ 错误: 缺少依赖包 - {e}")
        print("请运行: pip install -r requirements.txt")
        return False

async def start_polling_mode():
    """启动轮询模式"""
    print("🚀 启动轮询模式...")
    from bot import TelegramBot
    
    bot = TelegramBot()
    await bot.start_polling()

async def start_webhook_mode():
    """启动Webhook模式"""
    webhook_url = os.getenv('WEBHOOK_URL')
    if not webhook_url:
        print("❌ 错误: Webhook模式需要设置WEBHOOK_URL环境变量")
        return False
    
    print("🚀 启动Webhook模式...")
    from webhook_server import WebhookServer
    
    server = WebhookServer()
    await server.start_server()
    return True

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='Telegram Bot 启动脚本')
    parser.add_argument(
        '--mode', 
        choices=['polling', 'webhook'], 
        default='polling',
        help='运行模式: polling(轮询) 或 webhook(Webhook)'
    )
    parser.add_argument(
        '--check-only',
        action='store_true',
        help='仅检查环境配置，不启动机器人'
    )
    
    args = parser.parse_args()
    
    print("🤖 Telegram Bot 启动器")
    print("=" * 40)
    
    # 检查环境
    if not check_environment():
        sys.exit(1)
    
    # 检查依赖
    if not check_dependencies():
        sys.exit(1)
    
    if args.check_only:
        print("✅ 环境检查完成，机器人未启动")
        return
    
    # 启动机器人
    try:
        if args.mode == 'polling':
            asyncio.run(start_polling_mode())
        else:
            asyncio.run(start_webhook_mode())
    except KeyboardInterrupt:
        print("\n👋 机器人已停止")
    except Exception as e:
        print(f"❌ 启动失败: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()