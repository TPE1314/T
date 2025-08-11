#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Telegram Bot 项目健康检查脚本

这个脚本用于检查项目的整体健康状况，包括：
- 文件完整性检查
- 依赖包检查
- 配置验证
- 基本功能测试

使用方法:
    python health_check.py [选项]

选项:
    --quick     快速检查（跳过耗时测试）
    --full      完整检查（包含所有测试）
    --fix       自动修复发现的问题
    --verbose   详细输出
    --help      显示帮助信息
"""

import os
import sys
import importlib
import subprocess
import json
import time
from pathlib import Path
from typing import Dict, List, Tuple, Optional
import argparse
import logging

# 设置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class HealthChecker:
    """项目健康检查器"""
    
    def __init__(self, verbose: bool = False, auto_fix: bool = False):
        self.verbose = verbose
        self.auto_fix = auto_fix
        self.issues = []
        self.warnings = []
        self.fixes_applied = []
        self.project_root = Path(__file__).parent
        
        # 定义必需的文件和目录
        self.required_files = [
            'bot.py',
            'handlers.py',
            'config.py',
            'database.py',
            'admin_manager.py',
            'update_manager.py',
            'utils.py',
            'start_bot.py',
            'requirements.txt',
            'README.md',
            'DEPLOYMENT.md',
            'PROJECT_SUMMARY.md',
            'PROJECT_STRUCTURE.md',
            'COMPLETION_SUMMARY.md',
            'env_example.txt'
        ]
        
        self.required_dirs = [
            'monitoring'
        ]
        
        self.required_scripts = [
            'quick_start.sh',
            'quick_start.bat',
            'docker_deploy.sh',
            'docker_deploy.bat'
        ]
        
        self.docker_files = [
            'Dockerfile',
            'docker-compose.yml',
            '.dockerignore',
            'nginx.conf',
            'redis.conf'
        ]
    
    def log_issue(self, message: str, severity: str = "ERROR", fixable: bool = False):
        """记录问题"""
        issue = {
            'message': message,
            'severity': severity,
            'fixable': fixable,
            'timestamp': time.time()
        }
        self.issues.append(issue)
        
        if severity == "ERROR":
            logger.error(f"❌ {message}")
        elif severity == "WARNING":
            logger.warning(f"⚠️ {message}")
        else:
            logger.info(f"ℹ️ {message}")
    
    def log_warning(self, message: str):
        """记录警告"""
        self.log_issue(message, "WARNING")
    
    def log_fix(self, message: str):
        """记录修复"""
        self.fixes_applied.append(message)
        logger.info(f"🔧 已修复: {message}")
    
    def check_file_exists(self, file_path: str) -> bool:
        """检查文件是否存在"""
        full_path = self.project_root / file_path
        if not full_path.exists():
            self.log_issue(f"文件不存在: {file_path}", "ERROR", True)
            return False
        return True
    
    def check_directory_exists(self, dir_path: str) -> bool:
        """检查目录是否存在"""
        full_path = self.project_root / dir_path
        if not full_path.exists():
            self.log_issue(f"目录不存在: {dir_path}", "ERROR", True)
            return False
        return False
    
    def check_file_permissions(self, file_path: str) -> bool:
        """检查文件权限"""
        full_path = self.project_root / file_path
        if not full_path.exists():
            return False
        
        # 检查可执行权限（对于脚本文件）
        if file_path.endswith(('.sh', '.py')):
            if not os.access(full_path, os.X_OK):
                if self.auto_fix:
                    try:
                        os.chmod(full_path, 0o755)
                        self.log_fix(f"已设置执行权限: {file_path}")
                        return True
                    except Exception as e:
                        self.log_issue(f"无法设置执行权限 {file_path}: {e}", "ERROR", False)
                        return False
                else:
                    self.log_warning(f"文件缺少执行权限: {file_path}")
                    return False
        
        return True
    
    def check_python_syntax(self, file_path: str) -> bool:
        """检查Python文件语法"""
        if not file_path.endswith('.py'):
            return True
        
        full_path = self.project_root / file_path
        if not full_path.exists():
            return False
        
        try:
            with open(full_path, 'r', encoding='utf-8') as f:
                compile(f.read(), str(full_path), 'exec')
            return True
        except SyntaxError as e:
            self.log_issue(f"Python语法错误 {file_path}: {e}", "ERROR", False)
            return False
        except Exception as e:
            self.log_warning(f"无法检查Python语法 {file_path}: {e}")
            return False
    
    def check_imports(self, file_path: str) -> bool:
        """检查Python文件导入"""
        if not file_path.endswith('.py'):
            return True
        
        full_path = self.project_root / file_path
        if not full_path.exists():
            return False
        
        try:
            # 尝试导入模块
            module_name = file_path[:-3]  # 移除 .py 扩展名
            spec = importlib.util.spec_from_file_location(module_name, full_path)
            if spec is None:
                self.log_warning(f"无法加载模块规范: {file_path}")
                return False
            
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            return True
        except ImportError as e:
            self.log_warning(f"导入错误 {file_path}: {e}")
            return False
        except Exception as e:
            self.log_warning(f"模块加载错误 {file_path}: {e}")
            return False
    
    def check_requirements(self) -> bool:
        """检查依赖包"""
        requirements_file = self.project_root / 'requirements.txt'
        if not requirements_file.exists():
            self.log_issue("requirements.txt 文件不存在", "ERROR", True)
            return False
        
        try:
            with open(requirements_file, 'r', encoding='utf-8') as f:
                requirements = [line.strip() for line in f if line.strip() and not line.startswith('#')]
            
            if not requirements:
                self.log_issue("requirements.txt 文件为空", "ERROR", True)
                return False
            
            # 检查关键依赖
            critical_deps = ['python-telegram-bot', 'aiosqlite', 'aiohttp']
            missing_deps = []
            
            for dep in critical_deps:
                if not any(dep in req for req in requirements):
                    missing_deps.append(dep)
            
            if missing_deps:
                self.log_issue(f"缺少关键依赖: {', '.join(missing_deps)}", "ERROR", True)
                return False
            
            logger.info(f"✅ 依赖包检查通过，共 {len(requirements)} 个包")
            return True
            
        except Exception as e:
            self.log_issue(f"无法读取 requirements.txt: {e}", "ERROR", False)
            return False
    
    def check_config_template(self) -> bool:
        """检查配置模板"""
        env_file = self.project_root / 'env_example.txt'
        if not env_file.exists():
            self.log_issue("env_example.txt 文件不存在", "ERROR", True)
            return False
        
        try:
            with open(env_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 检查关键配置项
            required_configs = [
                'BOT_TOKEN',
                'ADMIN_IDS',
                'SUPER_ADMIN_ID',
                'DATABASE_URL'
            ]
            
            missing_configs = []
            for config in required_configs:
                if config not in content:
                    missing_configs.append(config)
            
            if missing_configs:
                self.log_issue(f"配置模板缺少关键项: {', '.join(missing_configs)}", "ERROR", True)
                return False
            
            logger.info("✅ 配置模板检查通过")
            return True
            
        except Exception as e:
            self.log_issue(f"无法读取配置模板: {e}", "ERROR", False)
            return False
    
    def check_docker_setup(self) -> bool:
        """检查Docker设置"""
        docker_compose = self.project_root / 'docker-compose.yml'
        if not docker_compose.exists():
            self.log_issue("docker-compose.yml 文件不存在", "ERROR", True)
            return False
        
        try:
            with open(docker_compose, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 检查关键服务
            required_services = ['bot', 'redis', 'nginx']
            missing_services = []
            
            for service in required_services:
                if service not in content:
                    missing_services.append(service)
            
            if missing_services:
                self.log_issue(f"Docker配置缺少关键服务: {', '.join(missing_services)}", "ERROR", True)
                return False
            
            logger.info("✅ Docker设置检查通过")
            return True
            
        except Exception as e:
            self.log_issue(f"无法读取Docker配置: {e}", "ERROR", False)
            return False
    
    def check_documentation(self) -> bool:
        """检查文档完整性"""
        required_docs = [
            'README.md',
            'DEPLOYMENT.md',
            'PROJECT_SUMMARY.md',
            'PROJECT_STRUCTURE.md',
            'COMPLETION_SUMMARY.md'
        ]
        
        missing_docs = []
        for doc in required_docs:
            if not (self.project_root / doc).exists():
                missing_docs.append(doc)
        
        if missing_docs:
            self.log_issue(f"缺少文档: {', '.join(missing_docs)}", "ERROR", True)
            return False
        
        logger.info("✅ 文档完整性检查通过")
        return True
    
    def check_script_permissions(self) -> bool:
        """检查脚本权限"""
        script_files = [f for f in self.required_scripts if f.endswith('.sh')]
        
        for script in script_files:
            if not self.check_file_permissions(script):
                return False
        
        logger.info("✅ 脚本权限检查通过")
        return True
    
    def run_quick_check(self) -> bool:
        """运行快速检查"""
        logger.info("🔍 开始快速健康检查...")
        
        checks = [
            ("文件完整性", self.check_file_integrity),
            ("依赖包", self.check_requirements),
            ("配置模板", self.check_config_template),
            ("文档完整性", self.check_documentation)
        ]
        
        all_passed = True
        for check_name, check_func in checks:
            try:
                if not check_func():
                    all_passed = False
            except Exception as e:
                self.log_issue(f"{check_name} 检查失败: {e}", "ERROR", False)
                all_passed = False
        
        return all_passed
    
    def run_full_check(self) -> bool:
        """运行完整检查"""
        logger.info("🔍 开始完整健康检查...")
        
        # 先运行快速检查
        if not self.run_quick_check():
            return False
        
        # 额外的完整检查
        additional_checks = [
            ("Docker设置", self.check_docker_setup),
            ("脚本权限", self.check_script_permissions),
            ("Python语法", self.check_python_syntax_all),
            ("模块导入", self.check_imports_all)
        ]
        
        all_passed = True
        for check_name, check_func in additional_checks:
            try:
                if not check_func():
                    all_passed = False
            except Exception as e:
                self.log_issue(f"{check_name} 检查失败: {e}", "ERROR", False)
                all_passed = False
        
        return all_passed
    
    def check_file_integrity(self) -> bool:
        """检查文件完整性"""
        logger.info("📁 检查文件完整性...")
        
        all_files_exist = True
        
        # 检查必需文件
        for file_path in self.required_files:
            if not self.check_file_exists(file_path):
                all_files_exist = False
        
        # 检查必需目录
        for dir_path in self.required_dirs:
            if not self.check_directory_exists(dir_path):
                all_files_exist = False
        
        # 检查脚本文件
        for script_path in self.required_scripts:
            if not self.check_file_exists(script_path):
                all_files_exist = False
        
        # 检查Docker文件
        for docker_file in self.docker_files:
            if not self.check_file_exists(docker_file):
                all_files_exist = False
        
        if all_files_exist:
            logger.info("✅ 文件完整性检查通过")
        else:
            logger.error("❌ 文件完整性检查失败")
        
        return all_files_exist
    
    def check_python_syntax_all(self) -> bool:
        """检查所有Python文件语法"""
        logger.info("🐍 检查Python文件语法...")
        
        python_files = [f for f in self.required_files if f.endswith('.py')]
        all_valid = True
        
        for py_file in python_files:
            if not self.check_python_syntax(py_file):
                all_valid = False
        
        if all_valid:
            logger.info("✅ Python语法检查通过")
        else:
            logger.error("❌ Python语法检查失败")
        
        return all_valid
    
    def check_imports_all(self) -> bool:
        """检查所有Python文件导入"""
        logger.info("📦 检查Python模块导入...")
        
        python_files = [f for f in self.required_files if f.endswith('.py')]
        all_valid = True
        
        for py_file in python_files:
            if not self.check_imports(py_file):
                all_valid = False
        
        if all_valid:
            logger.info("✅ Python模块导入检查通过")
        else:
            logger.error("❌ Python模块导入检查失败")
        
        return all_valid
    
    def generate_report(self) -> str:
        """生成健康检查报告"""
        total_issues = len(self.issues)
        errors = len([i for i in self.issues if i['severity'] == 'ERROR'])
        warnings = len([i for i in self.issues if i['severity'] == 'WARNING'])
        fixes = len(self.fixes_applied)
        
        report = f"""
📊 项目健康检查报告
{'='*50}

📈 总体状态:
  总问题数: {total_issues}
  错误: {errors} ❌
  警告: {warnings} ⚠️
  已修复: {fixes} 🔧

"""
        
        if errors == 0:
            report += "🎉 项目状态: 健康 ✅\n"
        elif errors <= 3:
            report += "⚠️ 项目状态: 需要注意 ⚠️\n"
        else:
            report += "❌ 项目状态: 需要修复 ❌\n"
        
        if self.issues:
            report += "\n📋 问题详情:\n"
            for i, issue in enumerate(self.issues, 1):
                status = "❌" if issue['severity'] == 'ERROR' else "⚠️"
                report += f"  {i}. {status} {issue['message']}\n"
        
        if self.fixes_applied:
            report += f"\n🔧 已修复的问题:\n"
            for fix in self.fixes_applied:
                report += f"  ✅ {fix}\n"
        
        report += f"\n⏰ 检查时间: {time.strftime('%Y-%m-%d %H:%M:%S')}"
        
        return report
    
    def run(self, check_type: str = "quick") -> bool:
        """运行健康检查"""
        start_time = time.time()
        
        try:
            if check_type == "quick":
                success = self.run_quick_check()
            else:
                success = self.run_full_check()
            
            duration = time.time() - start_time
            
            # 生成报告
            report = self.generate_report()
            print(report)
            
            if self.verbose:
                print(f"\n⏱️ 检查耗时: {duration:.2f}秒")
            
            return success
            
        except Exception as e:
            logger.error(f"健康检查过程中发生错误: {e}")
            return False

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="Telegram Bot 项目健康检查脚本")
    parser.add_argument("--quick", action="store_true", help="快速检查（默认）")
    parser.add_argument("--full", action="store_true", help="完整检查")
    parser.add_argument("--fix", action="store_true", help="自动修复发现的问题")
    parser.add_argument("--verbose", "-v", action="store_true", help="详细输出")
    
    args = parser.parse_args()
    
    # 确定检查类型
    check_type = "full" if args.full else "quick"
    
    # 创建健康检查器
    checker = HealthChecker(verbose=args.verbose, auto_fix=args.fix)
    
    # 运行检查
    success = checker.run(check_type)
    
    # 返回适当的退出码
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()