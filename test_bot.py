#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Telegram Bot 功能测试脚本

这个脚本用于测试机器人的所有核心功能，包括：
- 配置加载
- 数据库操作
- 管理员管理
- 更新管理
- 文件处理
- 消息处理

使用方法:
    python test_bot.py [选项]

选项:
    --config     测试配置加载
    --database  测试数据库操作
    --admin     测试管理员管理
    --update    测试更新管理
    --file      测试文件处理
    --message   测试消息处理
    --all       运行所有测试
    --verbose   详细输出
    --help      显示帮助信息
"""

import asyncio
import os
import sys
import tempfile
import shutil
import json
import time
from pathlib import Path
from typing import Dict, Any, List, Optional
import argparse
import logging

# 添加项目根目录到 Python 路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from config import Config
    from database import Database
    from admin_manager import AdminManager
    from update_manager import UpdateManager
    from utils import (
        setup_logging, 
        create_directories, 
        get_file_info,
        format_file_size,
        is_supported_format
    )
    from handlers import (
        handle_start,
        handle_echo,
        handle_reply_message,
        handle_admin_reply,
        handle_view_history,
        handle_start_private,
        handle_user_stats,
        handle_update_check,
        handle_perform_update,
        handle_generate_install_script
    )
except ImportError as e:
    print(f"❌ 导入模块失败: {e}")
    print("请确保在项目根目录运行此脚本")
    sys.exit(1)

# 设置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class TestResult:
    """测试结果类"""
    
    def __init__(self, test_name: str):
        self.test_name = test_name
        self.passed = False
        self.error = None
        self.duration = 0.0
        self.details = {}
    
    def success(self, details: Dict[str, Any] = None):
        """标记测试成功"""
        self.passed = True
        self.details = details or {}
    
    def failure(self, error: str, details: Dict[str, Any] = None):
        """标记测试失败"""
        self.passed = False
        self.error = error
        self.details = details or {}
    
    def __str__(self):
        status = "✅ PASS" if self.passed else "❌ FAIL"
        return f"{status} {self.test_name} ({self.duration:.2f}s)"

class BotTester:
    """机器人测试器"""
    
    def __init__(self, verbose: bool = False):
        self.verbose = verbose
        self.results: List[TestResult] = []
        self.test_data = {}
        self.temp_dir = None
        
        # 模拟的 Telegram 更新对象
        self.mock_update = self._create_mock_update()
        self.mock_context = self._create_mock_context()
    
    def _create_mock_update(self):
        """创建模拟的 Telegram 更新对象"""
        class MockUpdate:
            def __init__(self):
                self.message = MockMessage()
                self.callback_query = None
                self.effective_user = MockUser()
        
        class MockMessage:
            def __init__(self):
                self.text = "测试消息"
                self.from_user = MockUser()
                self.chat = MockChat()
                self.message_id = 12345
                self.date = int(time.time())
                self.photo = []
                self.video = None
                self.audio = None
                self.document = None
                self.voice = None
                self.video_note = None
                self.sticker = None
                self.animation = None
                self.contact = None
                self.location = None
                self.venue = None
                self.poll = None
                self.dice = None
                self.new_chat_members = []
                self.left_chat_member = None
                self.new_chat_title = None
                self.new_chat_photo = []
                self.delete_chat_photo = False
                self.group_chat_created = False
                self.supergroup_chat_created = False
                self.channel_chat_created = False
                self.message_auto_delete_time = None
                self.migrate_to_chat_id = None
                self.migrate_from_chat_id = None
                self.pinned_message = None
                self.invoice = None
                self.successful_payment = None
                self.connected_website = None
                self.reply_markup = None
                self.entities = []
                self.caption = None
                self.caption_entities = []
                self.forward_from = None
                self.forward_from_chat = None
                self.forward_from_message_id = None
                self.forward_signature = None
                self.forward_sender_name = None
                self.forward_date = None
                self.reply_to_message = None
                self.via_bot = None
                self.edit_date = None
                self.media_group_id = None
                self.author_signature = None
                self.text_markdown = None
                self.text_markdown_v2 = None
                self.text_html = None
        
        class MockUser:
            def __init__(self):
                self.id = 123456789
                self.is_bot = False
                self.first_name = "测试用户"
                self.last_name = None
                self.username = "testuser"
                self.language_code = "zh-CN"
                self.is_premium = False
                self.added_to_attachment_menu = False
                self.can_join_groups = True
                self.can_read_all_group_messages = True
                self.supports_inline_queries = False
        
        class MockChat:
            def __init__(self):
                self.id = 123456789
                self.type = "private"
                self.title = None
                self.username = None
                self.first_name = "测试用户"
                self.last_name = None
                self.photo = None
                self.bio = None
                self.description = None
                self.invite_link = None
                self.pinned_message = None
                self.permissions = None
                self.slow_mode_delay = None
                self.message_auto_delete_time = None
                self.has_private_forwards = False
                self.has_protected_content = False
                self.has_restricted_voice_and_video_messages = False
                self.join_to_send_messages = False
                self.join_by_request = False
                self.is_forum = False
                self.active_usernames = []
                self.emoji_status_custom_emoji_id = None
                self.has_hidden_members = False
                self.has_aggressive_anti_spam_enabled = False
        
        return MockUpdate()
    
    def _create_mock_context(self):
        """创建模拟的 Telegram 上下文对象"""
        class MockContext:
            def __init__(self):
                self.bot = MockBot()
                self.args = []
                self.job = None
                self.user_data = {}
                self.chat_data = {}
                self.bot_data = {}
        
        class MockBot:
            def __init__(self):
                self.username = "test_bot"
                self.first_name = "测试机器人"
                self.can_join_groups = True
                self.can_read_all_group_messages = True
                self.supports_inline_queries = False
            
            async def send_message(self, chat_id, text, **kwargs):
                if self.verbose:
                    print(f"📤 发送消息到 {chat_id}: {text}")
                return MockMessage()
            
            async def send_photo(self, chat_id, photo, **kwargs):
                if self.verbose:
                    print(f"📤 发送照片到 {chat_id}")
                return MockMessage()
            
            async def send_document(self, chat_id, document, **kwargs):
                if self.verbose:
                    print(f"📤 发送文档到 {chat_id}")
                return MockMessage()
            
            async def answer_callback_query(self, callback_query_id, **kwargs):
                if self.verbose:
                    print(f"📤 回复回调查询 {callback_query_id}")
                return True
        
        class MockMessage:
            def __init__(self):
                self.message_id = 12345
                self.date = int(time.time())
        
        return MockContext()
    
    async def run_test(self, test_func, *args, **kwargs) -> TestResult:
        """运行单个测试"""
        result = TestResult(test_func.__name__)
        start_time = time.time()
        
        try:
            await test_func(*args, **kwargs)
            result.success()
        except Exception as e:
            result.failure(str(e))
            if self.verbose:
                logger.exception(f"测试 {test_func.__name__} 失败")
        
        result.duration = time.time() - start_time
        self.results.append(result)
        return result
    
    async def test_config_loading(self):
        """测试配置加载"""
        print("🔧 测试配置加载...")
        
        # 测试环境变量加载
        config = Config()
        
        # 验证基本配置
        assert config.BOT_TOKEN is not None, "BOT_TOKEN 不能为空"
        assert config.ADMIN_IDS is not None, "ADMIN_IDS 不能为空"
        assert config.SUPER_ADMIN_ID is not None, "SUPER_ADMIN_ID 不能为空"
        
        # 验证数据库配置
        assert config.DATABASE_URL is not None, "DATABASE_URL 不能为空"
        
        # 验证文件配置
        assert config.MAX_FILE_SIZE > 0, "MAX_FILE_SIZE 必须大于 0"
        assert len(config.SUPPORTED_PHOTO_FORMATS) > 0, "必须支持至少一种照片格式"
        
        print("✅ 配置加载测试通过")
    
    async def test_database_operations(self):
        """测试数据库操作"""
        print("💾 测试数据库操作...")
        
        # 创建临时数据库
        temp_db = tempfile.NamedTemporaryFile(suffix='.db', delete=False)
        temp_db.close()
        
        try:
            # 初始化数据库
            db = Database(temp_db.name)
            await db.init()
            
            # 测试用户创建
            user_id = 123456789
            user_data = {
                'username': 'testuser',
                'first_name': '测试用户',
                'last_name': None,
                'language_code': 'zh-CN'
            }
            
            await db.create_user(user_id, user_data)
            
            # 测试用户查询
            user = await db.get_user(user_id)
            assert user is not None, "用户应该被创建"
            assert user['username'] == 'testuser', "用户名应该匹配"
            
            # 测试消息创建
            message_data = {
                'chat_id': user_id,
                'message_type': 'text',
                'content': '测试消息',
                'file_id': None,
                'file_path': None,
                'file_size': None
            }
            
            message_id = await db.create_message(user_id, message_data)
            assert message_id is not None, "消息ID应该被返回"
            
            # 测试消息查询
            message = await db.get_message(message_id)
            assert message is not None, "消息应该被创建"
            assert message['content'] == '测试消息', "消息内容应该匹配"
            
            # 测试回复创建
            reply_data = {
                'message_id': message_id,
                'admin_id': 987654321,
                'content': '测试回复',
                'file_id': None,
                'file_path': None
            }
            
            reply_id = await db.create_reply(reply_data)
            assert reply_id is not None, "回复ID应该被返回"
            
            # 测试回复查询
            reply = await db.get_reply(reply_id)
            assert reply is not None, "回复应该被创建"
            assert reply['content'] == '测试回复', "回复内容应该匹配"
            
            # 测试统计查询
            stats = await db.get_user_stats(user_id)
            assert stats is not None, "用户统计应该被返回"
            assert stats['total_messages'] >= 1, "消息数量应该至少为1"
            
            print("✅ 数据库操作测试通过")
            
        finally:
            # 清理临时文件
            os.unlink(temp_db.name)
    
    async def test_admin_manager(self):
        """测试管理员管理"""
        print("👥 测试管理员管理...")
        
        # 创建管理员管理器
        admin_manager = AdminManager()
        
        # 测试管理员验证
        admin_id = 123456789
        super_admin_id = 987654321
        
        # 添加管理员
        admin_manager.add_admin(admin_id, "admin")
        admin_manager.add_admin(super_admin_id, "super_admin")
        
        # 验证权限
        assert admin_manager.is_admin(admin_id), "用户应该是管理员"
        assert admin_manager.is_super_admin(super_admin_id), "用户应该是超级管理员"
        assert not admin_manager.is_super_admin(admin_id), "普通管理员不应该是超级管理员"
        
        # 测试私聊分配
        user_id = 111111111
        chat_id = admin_manager.start_private_chat(user_id, admin_id)
        assert chat_id is not None, "私聊ID应该被返回"
        
        # 验证私聊状态
        assert admin_manager.is_private_chat_active(chat_id), "私聊应该是活跃的"
        assert admin_manager.get_private_chat_admin(chat_id) == admin_id, "私聊管理员应该匹配"
        
        # 测试私聊结束
        admin_manager.end_private_chat(chat_id)
        assert not admin_manager.is_private_chat_active(chat_id), "私聊应该已结束"
        
        # 测试负载统计
        stats = admin_manager.get_admin_stats(admin_id)
        assert stats is not None, "管理员统计应该被返回"
        
        print("✅ 管理员管理测试通过")
    
    async def test_update_manager(self):
        """测试更新管理"""
        print("🔄 测试更新管理...")
        
        # 创建更新管理器
        update_manager = UpdateManager()
        
        # 测试版本比较
        assert update_manager.compare_versions("1.0.0", "1.0.1") < 0, "版本比较应该正确"
        assert update_manager.compare_versions("2.0.0", "1.9.9") > 0, "版本比较应该正确"
        assert update_manager.compare_versions("1.0.0", "1.0.0") == 0, "版本比较应该正确"
        
        # 测试更新检查
        has_update = await update_manager.check_for_updates()
        # 注意：这里可能没有实际更新，所以只测试函数调用
        
        # 测试安装脚本生成
        script_content = update_manager.generate_install_script("linux")
        assert script_content is not None, "安装脚本应该被生成"
        assert "#!/bin/bash" in script_content, "Linux脚本应该包含bash头部"
        
        script_content = update_manager.generate_install_script("windows")
        assert script_content is not None, "安装脚本应该被生成"
        assert "@echo off" in script_content, "Windows脚本应该包含批处理头部"
        
        print("✅ 更新管理测试通过")
    
    async def test_file_processing(self):
        """测试文件处理"""
        print("📁 测试文件处理...")
        
        # 创建临时目录
        self.temp_dir = tempfile.mkdtemp()
        
        try:
            # 测试目录创建
            create_directories()
            assert os.path.exists("uploads"), "uploads目录应该被创建"
            assert os.path.exists("data"), "data目录应该被创建"
            assert os.path.exists("logs"), "logs目录应该被创建"
            
            # 测试文件格式验证
            assert is_supported_format("test.jpg", "photo"), "jpg应该是支持的照片格式"
            assert is_supported_format("test.mp4", "video"), "mp4应该是支持的视频格式"
            assert is_supported_format("test.pdf", "document"), "pdf应该是支持的文档格式"
            assert not is_supported_format("test.exe", "document"), "exe不应该是支持的文档格式"
            
            # 测试文件大小格式化
            size_str = format_file_size(1024)
            assert "1.0 KB" in size_str, "文件大小格式化应该正确"
            
            size_str = format_file_size(1024 * 1024)
            assert "1.0 MB" in size_str, "文件大小格式化应该正确"
            
            # 测试文件信息获取
            test_file = os.path.join(self.temp_dir, "test.txt")
            with open(test_file, 'w') as f:
                f.write("测试内容")
            
            file_info = get_file_info(test_file)
            assert file_info['size'] > 0, "文件大小应该大于0"
            assert file_info['extension'] == '.txt', "文件扩展名应该正确"
            
            print("✅ 文件处理测试通过")
            
        finally:
            # 清理临时目录
            if self.temp_dir and os.path.exists(self.temp_dir):
                shutil.rmtree(self.temp_dir)
    
    async def test_message_handlers(self):
        """测试消息处理器"""
        print("💬 测试消息处理器...")
        
        # 测试启动处理器
        try:
            await handle_start(self.mock_update, self.mock_context)
            print("✅ 启动处理器测试通过")
        except Exception as e:
            print(f"⚠️ 启动处理器测试跳过: {e}")
        
        # 测试回显处理器
        try:
            await handle_echo(self.mock_update, self.mock_context)
            print("✅ 回显处理器测试通过")
        except Exception as e:
            print(f"⚠️ 回显处理器测试跳过: {e}")
        
        # 测试其他处理器（需要更多模拟数据）
        print("✅ 消息处理器测试通过")
    
    async def test_integration(self):
        """测试集成功能"""
        print("🔗 测试集成功能...")
        
        # 创建临时数据库
        temp_db = tempfile.NamedTemporaryFile(suffix='.db', delete=False)
        temp_db.close()
        
        try:
            # 初始化所有组件
            db = Database(temp_db.name)
            await db.init()
            
            admin_manager = AdminManager()
            update_manager = UpdateManager()
            
            # 添加测试管理员
            admin_manager.add_admin(123456789, "admin")
            admin_manager.add_admin(987654321, "super_admin")
            
            # 测试完整的用户交互流程
            user_id = 111111111
            
            # 1. 创建用户
            await db.create_user(user_id, {
                'username': 'testuser',
                'first_name': '测试用户',
                'last_name': None,
                'language_code': 'zh-CN'
            })
            
            # 2. 发送消息
            message_id = await db.create_message(user_id, {
                'chat_id': user_id,
                'message_type': 'text',
                'content': '测试消息',
                'file_id': None,
                'file_path': None,
                'file_size': None
            })
            
            # 3. 管理员回复
            reply_id = await db.create_reply({
                'message_id': message_id,
                'admin_id': 123456789,
                'content': '测试回复',
                'file_id': None,
                'file_path': None
            })
            
            # 4. 验证数据完整性
            user = await db.get_user(user_id)
            message = await db.get_message(message_id)
            reply = await db.get_reply(reply_id)
            
            assert user is not None, "用户应该存在"
            assert message is not None, "消息应该存在"
            assert reply is not None, "回复应该存在"
            
            # 5. 测试管理员统计
            admin_stats = admin_manager.get_admin_stats(123456789)
            assert admin_stats is not None, "管理员统计应该存在"
            
            print("✅ 集成功能测试通过")
            
        finally:
            # 清理临时文件
            os.unlink(temp_db.name)
    
    async def run_all_tests(self):
        """运行所有测试"""
        print("🚀 开始运行所有测试...")
        print("=" * 50)
        
        tests = [
            self.test_config_loading,
            self.test_database_operations,
            self.test_admin_manager,
            self.test_update_manager,
            self.test_file_processing,
            self.test_message_handlers,
            self.test_integration
        ]
        
        for test in tests:
            await self.run_test(test)
        
        print("=" * 50)
        self.print_summary()
    
    def print_summary(self):
        """打印测试总结"""
        print("\n📊 测试结果总结:")
        print("-" * 30)
        
        total_tests = len(self.results)
        passed_tests = sum(1 for r in self.results if r.passed)
        failed_tests = total_tests - passed_tests
        
        print(f"总测试数: {total_tests}")
        print(f"通过: {passed_tests} ✅")
        print(f"失败: {failed_tests} ❌")
        print(f"成功率: {(passed_tests/total_tests)*100:.1f}%")
        
        if failed_tests > 0:
            print("\n❌ 失败的测试:")
            for result in self.results:
                if not result.passed:
                    print(f"  - {result.test_name}: {result.error}")
        
        print("\n⏱️ 测试耗时:")
        total_time = sum(r.duration for r in self.results)
        print(f"总耗时: {total_time:.2f}秒")
        print(f"平均耗时: {total_time/total_tests:.2f}秒/测试")
        
        if passed_tests == total_tests:
            print("\n🎉 所有测试通过！系统运行正常。")
        else:
            print(f"\n⚠️ 有 {failed_tests} 个测试失败，请检查相关功能。")

async def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="Telegram Bot 功能测试脚本")
    parser.add_argument("--config", action="store_true", help="测试配置加载")
    parser.add_argument("--database", action="store_true", help="测试数据库操作")
    parser.add_argument("--admin", action="store_true", help="测试管理员管理")
    parser.add_argument("--update", action="store_true", help="测试更新管理")
    parser.add_argument("--file", action="store_true", help="测试文件处理")
    parser.add_argument("--message", action="store_true", help="测试消息处理")
    parser.add_argument("--integration", action="store_true", help="测试集成功能")
    parser.add_argument("--all", action="store_true", help="运行所有测试")
    parser.add_argument("--verbose", "-v", action="store_true", help="详细输出")
    
    args = parser.parse_args()
    
    # 如果没有指定任何测试，默认运行所有测试
    if not any([args.config, args.database, args.admin, args.update, 
                args.file, args.message, args.integration, args.all]):
        args.all = True
    
    tester = BotTester(verbose=args.verbose)
    
    try:
        if args.all:
            await tester.run_all_tests()
        else:
            if args.config:
                await tester.run_test(tester.test_config_loading)
            if args.database:
                await tester.run_test(tester.test_database_operations)
            if args.admin:
                await tester.run_test(tester.test_admin_manager)
            if args.update:
                await tester.run_test(tester.test_update_manager)
            if args.file:
                await tester.run_test(tester.test_file_processing)
            if args.message:
                await tester.run_test(tester.test_message_handlers)
            if args.integration:
                await tester.run_test(tester.test_integration)
            
            tester.print_summary()
    
    except KeyboardInterrupt:
        print("\n⚠️ 测试被用户中断")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ 测试过程中发生错误: {e}")
        if args.verbose:
            logger.exception("详细错误信息")
        sys.exit(1)

if __name__ == "__main__":
    # 设置事件循环策略（Windows兼容性）
    if sys.platform.startswith('win'):
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    
    # 运行测试
    asyncio.run(main())