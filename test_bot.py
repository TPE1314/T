#!/usr/bin/env python3
"""
Telegram Bot 测试脚本
用于测试机器人的基本功能
"""

import asyncio
import os
import sys
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

async def test_bot_creation():
    """测试机器人创建"""
    try:
        from bot import TelegramBot
        bot = TelegramBot()
        print("✅ 机器人创建成功")
        return True
    except Exception as e:
        print(f"❌ 机器人创建失败: {e}")
        return False

async def test_config():
    """测试配置加载"""
    try:
        import config
        print(f"✅ 配置加载成功")
        print(f"   - 上传目录: {config.UPLOAD_FOLDER}")
        print(f"   - 最大文件大小: {config.MAX_FILE_SIZE // (1024*1024)}MB")
        print(f"   - 支持图片格式: {', '.join(config.SUPPORTED_PHOTO_FORMATS)}")
        return True
    except Exception as e:
        print(f"❌ 配置加载失败: {e}")
        return False

async def test_handlers():
    """测试处理器导入"""
    try:
        from handlers import (
            handle_start, handle_help, handle_echo, handle_photo, handle_video,
            handle_audio, handle_document, handle_voice, handle_sticker,
            handle_animation, handle_contact, handle_location
        )
        print("✅ 处理器导入成功")
        return True
    except Exception as e:
        print(f"❌ 处理器导入失败: {e}")
        return False

async def test_utils():
    """测试工具函数"""
    try:
        from utils import (
            get_file_extension, is_supported_file_type, format_file_size,
            generate_filename, ensure_directory_exists
        )
        print("✅ 工具函数导入成功")
        
        # 测试基本功能
        assert get_file_extension("test.jpg") == ".jpg"
        assert is_supported_file_type("test.jpg")[0] == True
        assert format_file_size(1024) == "1.0 KB"
        
        print("✅ 工具函数测试通过")
        return True
    except Exception as e:
        print(f"❌ 工具函数测试失败: {e}")
        return False

async def test_webhook_server():
    """测试Webhook服务器"""
    try:
        from webhook_server import WebhookServer
        print("✅ Webhook服务器导入成功")
        return True
    except Exception as e:
        print(f"❌ Webhook服务器导入失败: {e}")
        return False

async def test_environment():
    """测试环境变量"""
    bot_token = os.getenv('BOT_TOKEN')
    if bot_token and bot_token != 'your_bot_token_here':
        print("✅ 环境变量配置正确")
        return True
    else:
        print("❌ 环境变量配置错误")
        print("请确保已设置正确的BOT_TOKEN")
        return False

async def run_all_tests():
    """运行所有测试"""
    print("🧪 开始运行测试...")
    print("=" * 50)
    
    tests = [
        ("环境变量", test_environment),
        ("配置加载", test_config),
        ("机器人创建", test_bot_creation),
        ("处理器导入", test_handlers),
        ("工具函数", test_utils),
        ("Webhook服务器", test_webhook_server),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n🔍 测试: {test_name}")
        try:
            if await test_func():
                passed += 1
                print(f"✅ {test_name} 测试通过")
            else:
                print(f"❌ {test_name} 测试失败")
        except Exception as e:
            print(f"❌ {test_name} 测试异常: {e}")
    
    print("\n" + "=" * 50)
    print(f"📊 测试结果: {passed}/{total} 通过")
    
    if passed == total:
        print("🎉 所有测试通过！机器人可以正常使用。")
        return True
    else:
        print("⚠️ 部分测试失败，请检查配置和依赖。")
        return False

def main():
    """主函数"""
    print("🤖 Telegram Bot 测试脚本")
    print("=" * 50)
    
    # 检查Python版本
    if sys.version_info < (3, 7):
        print("❌ 错误: 需要Python 3.7或更高版本")
        sys.exit(1)
    
    print(f"✅ Python版本: {sys.version}")
    
    # 运行测试
    try:
        success = asyncio.run(run_all_tests())
        if success:
            print("\n🚀 机器人测试完成，可以开始使用！")
            print("\n使用方法:")
            print("1. 轮询模式: python start_bot.py --mode polling")
            print("2. Webhook模式: python start_bot.py --mode webhook")
            print("3. 仅检查环境: python start_bot.py --check-only")
        else:
            print("\n⚠️ 测试发现问题，请修复后重试")
            sys.exit(1)
    except KeyboardInterrupt:
        print("\n👋 测试被中断")
    except Exception as e:
        print(f"\n❌ 测试运行失败: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()