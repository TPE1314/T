@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

REM Telegram Bot Docker 部署脚本 (Windows)
REM 适用于 Windows 系统

set "SCRIPT_NAME=%~n0"
set "SCRIPT_DIR=%~dp0"

REM 颜色定义
set "RED=[91m"
set "GREEN=[92m"
set "YELLOW=[93m"
set "BLUE=[94m"
set "NC=[0m"

REM 日志函数
:log_info
echo %BLUE%[INFO]%NC% %~1
goto :eof

:log_success
echo %GREEN%[SUCCESS]%NC% %~1
goto :eof

:log_warning
echo %YELLOW%[WARNING]%NC% %~1
goto :eof

:log_error
echo %RED%[ERROR]%NC% %~1
goto :eof

REM 检查Docker是否安装
:check_docker
docker --version >nul 2>&1
if errorlevel 1 (
    call :log_error "Docker 未安装，请先安装 Docker Desktop"
    pause
    exit /b 1
)

docker-compose --version >nul 2>&1
if errorlevel 1 (
    call :log_error "Docker Compose 未安装，请先安装 Docker Compose"
    pause
    exit /b 1
)

call :log_success "Docker 环境检查通过"
goto :eof

REM 检查配置文件
:check_config
if not exist ".env" (
    if exist "env_example.txt" (
        call :log_warning "未找到 .env 配置文件，正在创建..."
        copy env_example.txt .env >nul
        call :log_warning "请编辑 .env 文件，填入正确的配置信息"
        call :log_warning "特别是 BOT_TOKEN、ADMIN_IDS 和 SUPER_ADMIN_ID"
        pause
    ) else (
        call :log_error "未找到配置文件模板 env_example.txt"
        pause
        exit /b 1
    )
)

REM 检查必要的配置（简化版本）
findstr "BOT_TOKEN" .env >nul
if errorlevel 1 (
    call :log_error "请在 .env 文件中设置 BOT_TOKEN"
    pause
    exit /b 1
)

call :log_success "配置文件检查通过"
goto :eof

REM 创建必要的目录
:create_directories
call :log_info "创建必要的目录..."
if not exist "uploads" mkdir uploads
if not exist "data" mkdir data
if not exist "updates" mkdir updates
if not exist "backups" mkdir backups
if not exist "logs" mkdir logs
if not exist "ssl" mkdir ssl
if not exist "monitoring" mkdir monitoring

call :log_success "目录创建完成"
goto :eof

REM 生成自签名SSL证书（用于测试）
:generate_ssl_cert
if not exist "ssl\cert.pem" (
    call :log_info "生成自签名SSL证书..."
    
    REM 检查OpenSSL是否可用
    openssl version >nul 2>&1
    if errorlevel 1 (
        call :log_warning "OpenSSL 未安装，跳过SSL证书生成"
        call :log_warning "请手动生成SSL证书或使用HTTP模式"
        goto :ssl_skip
    )
    
    REM 生成私钥
    openssl genrsa -out ssl\key.pem 2048
    if errorlevel 1 (
        call :log_warning "SSL私钥生成失败，跳过SSL证书生成"
        goto :ssl_skip
    )
    
    REM 生成证书
    openssl req -new -x509 -key ssl\key.pem -out ssl\cert.pem -days 365 -subj "/C=CN/ST=State/L=City/O=Organization/CN=localhost"
    if errorlevel 1 (
        call :log_warning "SSL证书生成失败，跳过SSL证书生成"
        goto :ssl_skip
    )
    
    call :log_success "SSL证书生成完成"
) else (
    call :log_info "SSL证书已存在"
)
:ssl_skip
goto :eof

REM 构建Docker镜像
:build_images
call :log_info "构建Docker镜像..."
docker-compose build --no-cache

if errorlevel 1 (
    call :log_error "Docker镜像构建失败"
    pause
    exit /b 1
)

call :log_success "Docker镜像构建完成"
goto :eof

REM 启动服务
:start_services
call :log_info "启动服务..."
docker-compose up -d

if errorlevel 1 (
    call :log_error "服务启动失败"
    pause
    exit /b 1
)

call :log_success "服务启动完成"
goto :eof

REM 检查服务状态
:check_services
call :log_info "检查服务状态..."
timeout /t 10 /nobreak >nul

REM 检查容器状态
docker-compose ps

REM 检查健康状态
call :log_info "检查服务健康状态..."

REM 检查Telegram Bot（简化版本）
call :log_info "Telegram Bot 服务启动中..."

REM 检查Redis
docker exec bot-redis redis-cli ping >nul 2>&1
if errorlevel 1 (
    call :log_warning "Redis 服务可能未完全启动"
) else (
    call :log_success "Redis 服务正常"
)

call :log_info "服务状态检查完成"
goto :eof

REM 显示服务信息
:show_service_info
call :log_info "服务部署完成！"
echo.
echo 🌐 服务访问地址：
echo    - HTTP:  http://localhost
echo    - HTTPS: https://localhost
echo    - Bot API: http://localhost:8443
echo    - Redis:  localhost:6379
echo    - 监控:   http://localhost:9090
echo.
echo 📁 数据目录：
echo    - 上传文件: .\uploads
echo    - 数据库:   .\data
echo    - 更新文件: .\updates
echo    - 备份文件: .\backups
echo    - 日志文件: .\logs
echo.
echo 🔧 常用命令：
echo    - 查看状态: docker-compose ps
echo    - 查看日志: docker-compose logs -f
echo    - 停止服务: docker-compose down
echo    - 重启服务: docker-compose restart
echo    - 更新服务: docker-compose pull ^&^& docker-compose up -d
echo.
echo ⚠️  注意：
echo    - 首次使用请确保 .env 配置正确
echo    - 生产环境请使用正式的SSL证书
echo    - 定期备份 data 目录
goto :eof

REM 停止服务
:stop_services
call :log_info "停止服务..."
docker-compose down
call :log_success "服务已停止"
goto :eof

REM 清理资源
:cleanup
call :log_info "清理Docker资源..."
docker-compose down -v --remove-orphans
docker system prune -f
call :log_success "清理完成"
goto :eof

REM 显示帮助信息
:show_help
echo 使用方法: %SCRIPT_NAME% [选项]
echo.
echo 选项:
echo   start     启动服务（默认）
echo   stop      停止服务
echo   restart   重启服务
echo   status    查看服务状态
echo   logs      查看服务日志
echo   build     重新构建镜像
echo   cleanup   清理资源
echo   help      显示此帮助信息
echo.
echo 示例:
echo   %SCRIPT_NAME%             启动服务
echo   %SCRIPT_NAME% start       启动服务
echo   %SCRIPT_NAME% stop        停止服务
echo   %SCRIPT_NAME% restart     重启服务
echo   %SCRIPT_NAME% status      查看状态
echo   %SCRIPT_NAME% logs        查看日志
echo   %SCRIPT_NAME% build       重新构建
echo   %SCRIPT_NAME% cleanup     清理资源
goto :eof

REM 主函数
:main
if "%1"=="" goto :start
if "%1"=="start" goto :start
if "%1"=="stop" goto :stop
if "%1"=="restart" goto :restart
if "%1"=="status" goto :status
if "%1"=="logs" goto :logs
if "%1"=="build" goto :build
if "%1"=="cleanup" goto :cleanup
if "%1"=="help" goto :show_help
if "%1"=="--help" goto :show_help
if "%1"=="-h" goto :show_help

call :log_error "未知选项: %1"
call :show_help
pause
exit /b 1

:start
call :log_info "🚀 开始部署 Telegram Bot..."
call :check_docker
call :check_config
call :create_directories
call :generate_ssl_cert
call :build_images
call :start_services
call :check_services
call :show_service_info
goto :end

:stop
call :stop_services
goto :end

:restart
call :log_info "🔄 重启服务..."
call :stop_services
timeout /t 2 /nobreak >nul
call :start_services
call :check_services
goto :end

:status
docker-compose ps
goto :end

:logs
docker-compose logs -f
goto :end

:build
call :check_docker
call :check_config
call :build_images
goto :end

:cleanup
call :cleanup
goto :end

:end
if "%1"=="" (
    echo.
    pause
)
exit /b 0