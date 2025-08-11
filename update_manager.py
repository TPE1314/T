import os
import json
import logging
import requests
import subprocess
import asyncio
from datetime import datetime
from typing import Optional, Dict, List
from dataclasses import dataclass
import config
from database import UpdateInfo, db

logger = logging.getLogger(__name__)

@dataclass
class UpdateCheckResult:
    """更新检查结果"""
    has_update: bool
    current_version: str
    latest_version: str
    description: str
    download_url: str
    is_forced: bool
    changelog: str
    release_date: str

class UpdateManager:
    """云更新管理器"""
    
    def __init__(self):
        self.current_version = "1.0.0"
        self.update_check_url = os.getenv('UPDATE_CHECK_URL', '')
        self.auto_update = os.getenv('AUTO_UPDATE', 'false').lower() == 'true'
        self.update_interval = int(os.getenv('UPDATE_INTERVAL', '3600'))  # 秒
        self.last_check = None
        
        # 从配置文件读取当前版本
        self.load_version_info()
    
    def load_version_info(self):
        """从配置文件加载版本信息"""
        try:
            if os.path.exists('version.json'):
                with open('version.json', 'r', encoding='utf-8') as f:
                    version_data = json.load(f)
                    self.current_version = version_data.get('version', '1.0.0')
        except Exception as e:
            logger.error(f"加载版本信息失败: {e}")
    
    def save_version_info(self, version: str):
        """保存版本信息"""
        try:
            version_data = {
                'version': version,
                'update_time': datetime.now().isoformat()
            }
            with open('version.json', 'w', encoding='utf-8') as f:
                json.dump(version_data, f, ensure_ascii=False, indent=2)
            self.current_version = version
        except Exception as e:
            logger.error(f"保存版本信息失败: {e}")
    
    async def check_for_updates(self) -> UpdateCheckResult:
        """检查更新"""
        try:
            if not self.update_check_url:
                return UpdateCheckResult(
                    has_update=False,
                    current_version=self.current_version,
                    latest_version=self.current_version,
                    description="",
                    download_url="",
                    is_forced=False,
                    changelog="",
                    release_date=""
                )
            
            # 从数据库获取最新更新信息
            latest_update = await db.get_latest_update()
            if not latest_update:
                return UpdateCheckResult(
                    has_update=False,
                    current_version=self.current_version,
                    latest_version=self.current_version,
                    description="",
                    download_url="",
                    is_forced=False,
                    changelog="",
                    release_date=""
                )
            
            # 比较版本
            has_update = self.compare_versions(self.current_version, latest_update.version)
            
            return UpdateCheckResult(
                has_update=has_update,
                current_version=self.current_version,
                latest_version=latest_update.version,
                description=latest_update.description,
                download_url=latest_update.download_url,
                is_forced=latest_update.is_forced,
                changelog=latest_update.changelog,
                release_date=latest_update.release_date
            )
            
        except Exception as e:
            logger.error(f"检查更新失败: {e}")
            return UpdateCheckResult(
                has_update=False,
                current_version=self.current_version,
                latest_version=self.current_version,
                description="",
                download_url="",
                is_forced=False,
                changelog="",
                release_date=""
            )
    
    def compare_versions(self, current: str, latest: str) -> bool:
        """比较版本号"""
        try:
            current_parts = [int(x) for x in current.split('.')]
            latest_parts = [int(x) for x in latest.split('.')]
            
            for i in range(max(len(current_parts), len(latest_parts))):
                current_part = current_parts[i] if i < len(current_parts) else 0
                latest_part = latest_parts[i] if i < len(latest_parts) else 0
                
                if latest_part > current_part:
                    return True
                elif latest_part < current_part:
                    return False
            
            return False
        except Exception as e:
            logger.error(f"版本比较失败: {e}")
            return False
    
    async def download_update(self, download_url: str) -> bool:
        """下载更新"""
        try:
            logger.info(f"开始下载更新: {download_url}")
            
            # 创建更新目录
            update_dir = "updates"
            os.makedirs(update_dir, exist_ok=True)
            
            # 下载文件
            response = requests.get(download_url, stream=True)
            response.raise_for_status()
            
            filename = download_url.split('/')[-1]
            file_path = os.path.join(update_dir, filename)
            
            with open(file_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            
            logger.info(f"更新下载完成: {file_path}")
            return True
            
        except Exception as e:
            logger.error(f"下载更新失败: {e}")
            return False
    
    async def install_update(self, file_path: str) -> bool:
        """安装更新"""
        try:
            logger.info(f"开始安装更新: {file_path}")
            
            # 根据文件类型选择安装方法
            if file_path.endswith('.py'):
                # Python脚本更新
                return await self.install_python_update(file_path)
            elif file_path.endswith('.sh'):
                # Shell脚本更新
                return await self.install_shell_update(file_path)
            elif file_path.endswith('.bat'):
                # Windows批处理更新
                return await self.install_batch_update(file_path)
            else:
                logger.warning(f"不支持的更新文件类型: {file_path}")
                return False
                
        except Exception as e:
            logger.error(f"安装更新失败: {e}")
            return False
    
    async def install_python_update(self, file_path: str) -> bool:
        """安装Python脚本更新"""
        try:
            # 备份当前文件
            backup_dir = "backups"
            os.makedirs(backup_dir, exist_ok=True)
            
            # 执行更新脚本
            result = subprocess.run([
                'python3', file_path
            ], capture_output=True, text=True, timeout=300)
            
            if result.returncode == 0:
                logger.info("Python更新安装成功")
                return True
            else:
                logger.error(f"Python更新安装失败: {result.stderr}")
                return False
                
        except Exception as e:
            logger.error(f"Python更新安装失败: {e}")
            return False
    
    async def install_shell_update(self, file_path: str) -> bool:
        """安装Shell脚本更新"""
        try:
            # 设置执行权限
            os.chmod(file_path, 0o755)
            
            # 执行更新脚本
            result = subprocess.run([
                'bash', file_path
            ], capture_output=True, text=True, timeout=300)
            
            if result.returncode == 0:
                logger.info("Shell更新安装成功")
                return True
            else:
                logger.error(f"Shell更新安装失败: {result.stderr}")
                return False
                
        except Exception as e:
            logger.error(f"Shell更新安装失败: {e}")
            return False
    
    async def install_batch_update(self, file_path: str) -> bool:
        """安装Windows批处理更新"""
        try:
            # 执行更新脚本
            result = subprocess.run([
                'cmd', '/c', file_path
            ], capture_output=True, text=True, timeout=300)
            
            if result.returncode == 0:
                logger.info("批处理更新安装成功")
                return True
            else:
                logger.error(f"批处理更新安装失败: {result.stderr}")
                return False
                
        except Exception as e:
            logger.error(f"批处理更新安装失败: {e}")
            return False
    
    async def auto_update_check(self):
        """自动更新检查"""
        while True:
            try:
                await asyncio.sleep(self.update_interval)
                
                logger.info("执行自动更新检查")
                update_result = await self.check_for_updates()
                
                if update_result.has_update:
                    logger.info(f"发现新版本: {update_result.latest_version}")
                    
                    if self.auto_update:
                        await self.perform_update(update_result)
                    else:
                        logger.info("自动更新已禁用，需要手动更新")
                        
            except Exception as e:
                logger.error(f"自动更新检查失败: {e}")
    
    async def perform_update(self, update_result: UpdateCheckResult) -> bool:
        """执行更新"""
        try:
            logger.info(f"开始执行更新: {update_result.latest_version}")
            
            # 下载更新
            if not await self.download_update(update_result.download_url):
                return False
            
            # 安装更新
            filename = update_result.download_url.split('/')[-1]
            file_path = os.path.join("updates", filename)
            
            if not await self.install_update(file_path):
                return False
            
            # 更新版本信息
            self.save_version_info(update_result.latest_version)
            
            logger.info(f"更新完成: {update_result.latest_version}")
            return True
            
        except Exception as e:
            logger.error(f"执行更新失败: {e}")
            return False
    
    async def add_update_info(self, version: str, description: str, 
                            download_url: str, is_forced: bool = False, 
                            changelog: str = "") -> bool:
        """添加更新信息"""
        try:
            update_info = UpdateInfo(
                version=version,
                description=description,
                download_url=download_url,
                release_date=datetime.now().isoformat(),
                is_forced=is_forced,
                changelog=changelog
            )
            
            return await db.add_update(update_info)
            
        except Exception as e:
            logger.error(f"添加更新信息失败: {e}")
            return False
    
    def get_update_script(self, platform: str = "linux") -> str:
        """生成一键安装脚本"""
        if platform == "linux":
            return self.get_linux_install_script()
        elif platform == "windows":
            return self.get_windows_install_script()
        else:
            return self.get_linux_install_script()
    
    def get_linux_install_script(self) -> str:
        """生成Linux安装脚本"""
        script = '''#!/bin/bash

# Telegram Bot 一键安装脚本
# 适用于 Ubuntu/Debian 系统

set -e

echo "🚀 开始安装 Telegram Bot..."

# 检查系统
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 未安装，正在安装..."
    sudo apt update
    sudo apt install -y python3 python3-pip python3-venv
fi

# 检查 git
if ! command -v git &> /dev/null; then
    echo "📦 安装 Git..."
    sudo apt install -y git
fi

# 创建项目目录
PROJECT_DIR="$HOME/telegram-bot"
if [ -d "$PROJECT_DIR" ]; then
    echo "📁 项目目录已存在，正在备份..."
    mv "$PROJECT_DIR" "$PROJECT_DIR.backup.$(date +%Y%m%d_%H%M%S)"
fi

mkdir -p "$PROJECT_DIR"
cd "$PROJECT_DIR"

# 克隆项目（如果是从Git仓库）
# git clone <your-repo-url> .

# 创建虚拟环境
echo "🐍 创建 Python 虚拟环境..."
python3 -m venv venv
source venv/bin/activate

# 安装依赖
echo "📦 安装依赖包..."
pip install --upgrade pip
pip install -r requirements.txt

# 创建配置文件
echo "⚙️ 创建配置文件..."
if [ ! -f ".env" ]; then
    cat > .env << EOF
# Telegram Bot 配置
BOT_TOKEN=your_bot_token_here
ADMIN_IDS=your_admin_id_here
SUPER_ADMIN_ID=your_super_admin_id_here

# 数据库配置
DATABASE_URL=data/bot.db

# 更新配置
UPDATE_CHECK_URL=your_update_url_here
AUTO_UPDATE=false
UPDATE_INTERVAL=3600

# 私聊配置
ENABLE_PRIVATE_CHAT=true
MAX_PRIVATE_CHATS_PER_ADMIN=10

# 文件上传配置
UPLOAD_FOLDER=uploads
MAX_FILE_SIZE=52428800
SUPPORTED_FORMATS=jpg,jpeg,png,gif,mp4,avi,mov,mp3,wav,pdf,doc,docx,txt

# Webhook 配置（可选）
WEBHOOK_URL=
WEBHOOK_PORT=8443
EOF
    echo "⚠️ 请编辑 .env 文件，填入正确的配置信息"
fi

# 创建必要目录
echo "📁 创建必要目录..."
mkdir -p data uploads updates backups

# 设置权限
chmod +x start_bot.py
chmod +x quick_start.sh

# 创建系统服务
echo "🔧 创建系统服务..."
sudo tee /etc/systemd/system/telegram-bot.service > /dev/null << EOF
[Unit]
Description=Telegram Bot Service
After=network.target

[Service]
Type=simple
User=$USER
WorkingDirectory=$PROJECT_DIR
Environment=PATH=$PROJECT_DIR/venv/bin
ExecStart=$PROJECT_DIR/venv/bin/python start_bot.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# 启用服务
sudo systemctl daemon-reload
sudo systemctl enable telegram-bot.service

echo "✅ 安装完成！"
echo ""
echo "📋 下一步操作："
echo "1. 编辑 .env 文件，填入正确的配置信息"
echo "2. 启动服务: sudo systemctl start telegram-bot.service"
echo "3. 查看状态: sudo systemctl status telegram-bot.service"
echo "4. 查看日志: sudo journalctl -u telegram-bot.service -f"
echo ""
echo "🔗 项目目录: $PROJECT_DIR"
echo "📚 查看帮助: python start_bot.py --help"
'''
        return script
    
    def get_windows_install_script(self) -> str:
        """生成Windows安装脚本"""
        script = '''@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

echo 🚀 开始安装 Telegram Bot...

REM 检查 Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python 未安装，请先安装 Python 3.7+
    pause
    exit /b 1
)

REM 检查 Git
git --version >nul 2>&1
if errorlevel 1 (
    echo 📦 安装 Git...
    echo 请访问 https://git-scm.com/download/win 下载并安装 Git
    pause
)

REM 创建项目目录
set PROJECT_DIR=%USERPROFILE%\\telegram-bot
if exist "%PROJECT_DIR%" (
    echo 📁 项目目录已存在，正在备份...
    ren "%PROJECT_DIR%" "telegram-bot.backup.%date:~0,4%%date:~5,2%%date:~8,2%_%time:~0,2%%time:~3,2%%time:~6,2%"
)
mkdir "%PROJECT_DIR%"
cd /d "%PROJECT_DIR%"

REM 创建虚拟环境
echo 🐍 创建 Python 虚拟环境...
python -m venv venv
call venv\\Scripts\\activate.bat

REM 安装依赖
echo 📦 安装依赖包...
python -m pip install --upgrade pip
pip install -r requirements.txt

REM 创建配置文件
echo ⚙️ 创建配置文件...
if not exist ".env" (
    (
        echo # Telegram Bot 配置
        echo BOT_TOKEN=your_bot_token_here
        echo ADMIN_IDS=your_admin_id_here
        echo SUPER_ADMIN_ID=your_super_admin_id_here
        echo.
        echo # 数据库配置
        echo DATABASE_URL=data/bot.db
        echo.
        echo # 更新配置
        echo UPDATE_CHECK_URL=your_update_url_here
        echo AUTO_UPDATE=false
        echo UPDATE_INTERVAL=3600
        echo.
        echo # 私聊配置
        echo ENABLE_PRIVATE_CHAT=true
        echo MAX_PRIVATE_CHATS_PER_ADMIN=10
        echo.
        echo # 文件上传配置
        echo UPLOAD_FOLDER=uploads
        echo MAX_FILE_SIZE=52428800
        echo SUPPORTED_FORMATS=jpg,jpeg,png,gif,mp4,avi,mov,mp3,wav,pdf,doc,docx,txt
        echo.
        echo # Webhook 配置（可选）
        echo WEBHOOK_URL=
        echo WEBHOOK_PORT=8443
    ) > .env
    echo ⚠️ 请编辑 .env 文件，填入正确的配置信息
)

REM 创建必要目录
echo 📁 创建必要目录...
mkdir data 2>nul
mkdir uploads 2>nul
mkdir updates 2>nul
mkdir backups 2>nul

REM 创建启动脚本
echo 🔧 创建启动脚本...
(
    echo @echo off
    echo cd /d "%PROJECT_DIR%"
    echo call venv\\Scripts\\activate.bat
    echo python start_bot.py
    echo pause
) > start_bot.bat

echo ✅ 安装完成！
echo.
echo 📋 下一步操作：
echo 1. 编辑 .env 文件，填入正确的配置信息
echo 2. 双击 start_bot.bat 启动机器人
echo 3. 或使用命令行: python start_bot.py
echo.
echo 🔗 项目目录: %PROJECT_DIR%
echo 📚 查看帮助: python start_bot.py --help
pause
'''
        return script

# 全局更新管理器实例
update_manager = UpdateManager()