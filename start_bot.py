#!/usr/bin/env python3
"""
Telegram Bot 启动脚本
支持多种启动模式和配置选项
"""

import asyncio
import argparse
import logging
import os
import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from bot import TelegramBot
import config

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('bot.log', encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

async def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='Telegram Bot 启动脚本')
    parser.add_argument('--mode', choices=['polling', 'webhook'], default='polling',
                       help='启动模式: polling 或 webhook (默认: polling)')
    parser.add_argument('--config', default='.env',
                       help='配置文件路径 (默认: .env)')
    parser.add_argument('--debug', action='store_true',
                       help='启用调试模式')
    parser.add_argument('--port', type=int, default=8443,
                       help='Webhook端口 (默认: 8443)')
    parser.add_argument('--host', default='0.0.0.0',
                       help='Webhook主机地址 (默认: 0.0.0.0)')
    
    args = parser.parse_args()
    
    # 设置调试模式
    if args.debug:
        logging.getLogger().setLevel(logging.DEBUG)
        logger.info("调试模式已启用")
    
    # 检查配置文件
    if not os.path.exists(args.config):
        logger.error(f"配置文件 {args.config} 不存在")
        logger.info("请复制 env_example.txt 为 .env 并填写配置")
        return 1
    
    # 检查必要的配置
    if not config.BOT_TOKEN:
        logger.error("BOT_TOKEN 未配置")
        return 1
    
    if not config.ADMIN_IDS:
        logger.error("ADMIN_IDS 未配置")
        return 1
    
    if not config.SUPER_ADMIN_ID:
        logger.error("SUPER_ADMIN_ID 未配置")
        return 1
    
    try:
        # 创建机器人实例
        bot = TelegramBot()
        logger.info("机器人初始化成功")
        
        if args.mode == 'polling':
            logger.info("启动轮询模式...")
            await bot.start_polling()
        else:
            logger.info(f"启动Webhook模式，监听 {args.host}:{args.port}")
            await bot.start_webhook(host=args.host, port=args.port)
            
    except KeyboardInterrupt:
        logger.info("收到中断信号，正在关闭机器人...")
    except Exception as e:
        logger.error(f"启动失败: {e}")
        return 1
    
    return 0

if __name__ == '__main__':
    try:
        exit_code = asyncio.run(main())
        sys.exit(exit_code)
    except KeyboardInterrupt:
        logger.info("程序被用户中断")
        sys.exit(0)
    except Exception as e:
        logger.error(f"程序异常退出: {e}")
        sys.exit(1)