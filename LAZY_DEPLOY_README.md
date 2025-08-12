# 🚀 Telegram Bot 懒人版一键部署

## 🎯 一句话说明
**直接在服务器上运行一个命令，就能完成所有部署！**

## 📱 使用方法

### 1. 下载脚本
```bash
wget https://raw.githubusercontent.com/your-repo/your-project/main/lazy_deploy.sh
```

### 2. 运行部署
```bash
chmod +x lazy_deploy.sh
./lazy_deploy.sh
```

**就这么简单！** 🎉

## 🔧 脚本特性

- ✅ **自动检测系统**：支持Ubuntu、CentOS、Debian等
- ✅ **自动检测用户**：支持root用户和普通用户
- ✅ **一键安装**：Python、Redis、Nginx等所有依赖
- ✅ **自动配置**：系统服务、防火墙、启动脚本
- ✅ **智能适配**：根据系统类型选择正确的包管理器
- ✅ **完整部署**：从零开始到运行，一步到位

## 🖥️ 支持的系统

| 系统 | 包管理器 | 状态 |
|------|----------|------|
| Ubuntu | apt | ✅ 完全支持 |
| Debian | apt | ✅ 完全支持 |
| CentOS | yum | ✅ 完全支持 |
| RHEL | yum | ✅ 完全支持 |
| Fedora | yum | ✅ 完全支持 |

## 👤 用户支持

- **root用户**：直接运行，无需sudo
- **普通用户**：自动使用sudo权限

## 📁 部署结果

脚本会自动创建以下内容：
- 项目目录：`/home/用户名/telegram-bot/` 或 `/root/telegram-bot/`
- Python虚拟环境
- 系统服务（systemd）
- 启动脚本
- 配置文件模板
- 防火墙规则

## 🚨 注意事项

1. **网络连接**：确保服务器能访问外网
2. **权限要求**：普通用户需要sudo权限
3. **Bot Token**：部署完成后需要编辑`.env`文件设置Token
4. **系统更新**：脚本会自动更新系统包

## 🔍 故障排除

如果遇到问题：

```bash
# 查看服务状态
sudo systemctl status telegram-bot

# 查看日志
sudo journalctl -u telegram-bot -f

# 重启服务
sudo systemctl restart telegram-bot
```

## 📞 技术支持

如果还有问题，请检查：
1. 系统是否为支持的Linux发行版
2. 网络连接是否正常
3. 用户是否有足够权限
4. 查看脚本输出的错误信息

---

**记住：一个命令搞定所有部署！** 🚀