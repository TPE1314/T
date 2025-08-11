import asyncio
import logging
from aiohttp import web
from telegram import Update
from telegram.ext import Application

import config
from bot import TelegramBot

# 配置日志
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

class WebhookServer:
    def __init__(self):
        self.bot = TelegramBot()
        self.app = web.Application()
        self.setup_routes()
    
    def setup_routes(self):
        """设置Web路由"""
        self.app.router.add_post(f'/{config.BOT_TOKEN}', self.handle_webhook)
        self.app.router.add_get('/', self.handle_root)
        self.app.router.add_get('/health', self.handle_health)
    
    async def handle_webhook(self, request):
        """处理Telegram Webhook请求"""
        try:
            # 获取更新数据
            update_data = await request.json()
            update = Update.de_json(update_data, self.bot.application.bot)
            
            # 处理更新
            await self.bot.application.process_update(update)
            
            return web.Response(status=200)
            
        except Exception as e:
            logger.error(f"处理Webhook时出错: {e}")
            return web.Response(status=500, text="Internal Server Error")
    
    async def handle_root(self, request):
        """处理根路径请求"""
        return web.Response(
            text="🤖 Telegram Bot Webhook Server\n\n状态: 运行中\n模式: Webhook",
            content_type='text/plain'
        )
    
    async def handle_health(self, request):
        """健康检查端点"""
        return web.json_response({
            "status": "healthy",
            "bot": "running",
            "mode": "webhook",
            "timestamp": asyncio.get_event_loop().time()
        })
    
    async def start_server(self):
        """启动Webhook服务器"""
        runner = web.AppRunner(self.app)
        await runner.setup()
        
        site = web.TCPSite(
            runner, 
            '0.0.0.0', 
            config.WEBHOOK_PORT
        )
        
        logger.info(f"启动Webhook服务器，监听端口 {config.WEBHOOK_PORT}")
        await site.start()
        
        # 设置Webhook URL
        webhook_url = f"{config.WEBHOOK_URL}/{config.BOT_TOKEN}"
        await self.bot.application.bot.set_webhook(url=webhook_url)
        logger.info(f"Webhook已设置: {webhook_url}")
        
        # 保持服务器运行
        try:
            await asyncio.Future()  # 无限等待
        except KeyboardInterrupt:
            logger.info("收到停止信号，正在关闭服务器...")
        finally:
            await runner.cleanup()

async def main():
    """主函数"""
    if not config.BOT_TOKEN:
        logger.error("未设置BOT_TOKEN环境变量")
        return
    
    if not config.WEBHOOK_URL:
        logger.error("未设置WEBHOOK_URL环境变量")
        return
    
    server = WebhookServer()
    await server.start_server()

if __name__ == "__main__":
    asyncio.run(main())