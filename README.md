# 手机监控系统 - 局域网直连版

## 📋 项目说明

这是一个基于Python的手机监控系统，支持在同一局域网内的两台设备之间直接通信，无需第三方服务器。

**⚠️ 重要提示：**
- 本工具仅供合法用途，如管理自己的设备
- 请确保您有权监控目标设备
- 不得用于非法监控他人设备

## 🎯 功能特性

### 已实现功能：
- ✅ 设备信息查看（CPU、内存、磁盘使用率）
- ✅ 屏幕截图
- ✅ 进程列表查看
- ✅ 文件浏览和读取
- ✅ 系统命令执行
- ✅ 网络信息查看
- ✅ 实时交互式控制

## 📦 安装依赖

### 基础依赖（必需）
```bash
# Python 3.6+
python --version
```

### 可选依赖（增强功能）
```bash
# 系统信息监控
pip install psutil

# 屏幕截图（Windows/Mac/Linux桌面）
pip install pillow

# Android设备额外依赖
pip install pydroid3  # 如果在Android上使用
```

## 🚀 使用方法

### 第一步：在被监控设备上启动服务端

1. 将 `server.py` 复制到备用手机/设备
2. 安装Python和依赖
3. 运行服务端：

```bash
python server.py
```

或指定端口：
```bash
python server.py 9999
```

4. 记下显示的IP地址，例如：`192.168.1.100`

### 第二步：在控制设备上运行客户端

1. 确保控制设备与被监控设备在同一局域网
2. 运行客户端：

```bash
python client.py 192.168.1.100
```

或指定端口：
```bash
python client.py 192.168.1.100 9999
```

### 第三步：使用交互式命令

连接成功后，可以使用以下命令：

```
> info              # 查看设备信息
> screenshot        # 截取屏幕
> processes         # 查看运行进程
> files             # 列出文件（默认用户目录）
> files /sdcard/    # 列出指定目录
> read /path/file   # 读取文件内容
> exec ls -la       # 执行系统命令
> network           # 查看网络信息
> ping              # 测试连接
> help              # 显示帮助
> exit              # 退出
```

## 📱 Android设备配置

### 方法1：使用Termux（推荐）

1. 安装Termux（从F-Droid下载）
2. 在Termux中安装Python：
```bash
pkg update
pkg install python
pip install psutil
```

3. 授予存储权限：
```bash
termux-setup-storage
```

4. 运行服务端：
```bash
python server.py
```

### 方法2：使用QPython

1. 安装QPython3
2. 将server.py导入到QPython
3. 运行脚本

### 方法3：使用Pydroid 3

1. 安装Pydroid 3
2. 安装依赖包
3. 运行server.py

## 🔧 网络配置

### 确保两台设备在同一网络：

1. **WiFi连接**：两台设备连接到同一个WiFi
2. **热点模式**：一台设备开热点，另一台连接
3. **USB网络共享**：通过USB连接并共享网络

### 查看设备IP地址：

**Android:**
```
设置 -> 关于手机 -> 状态 -> IP地址
```

**Windows:**
```bash
ipconfig
```

**Linux/Mac:**
```bash
ifconfig
# 或
ip addr
```

### 防火墙设置：

如果无法连接，需要允许端口通过防火墙：

**Windows:**
```bash
# 允许端口8888
netsh advfirewall firewall add rule name="Phone Monitor" dir=in action=allow protocol=TCP localport=8888
```

**Linux:**
```bash
# 使用ufw
sudo ufw allow 8888/tcp

# 或使用iptables
sudo iptables -A INPUT -p tcp --dport 8888 -j ACCEPT
```

**Android (需要root):**
```bash
# 通常不需要配置，Termux会自动处理
```

## 🔒 安全建议

1. **仅在可信网络使用**：不要在公共WiFi上使用
2. **修改默认端口**：使用非标准端口增加安全性
3. **添加认证**：可以修改代码添加密码验证
4. **加密通信**：可以使用SSL/TLS加密
5. **限制访问**：只允许特定IP连接

## 🛠️ 高级配置

### 添加密码认证

在server.py中添加：
```python
PASSWORD = "your_secure_password"

def handle_client(self, client_socket, address):
    # 首先验证密码
    auth_data = client_socket.recv(1024)
    if auth_data.decode() != PASSWORD:
        client_socket.close()
        return
    # ... 继续处理
```

### 使用SSL加密

```python
import ssl

# 服务端
context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
context.load_cert_chain('server.crt', 'server.key')
secure_socket = context.wrap_socket(server_socket, server_side=True)

# 客户端
context = ssl.create_default_context()
secure_socket = context.wrap_socket(socket, server_hostname=host)
```

### 后台运行服务端

**Linux/Android (Termux):**
```bash
nohup python server.py > server.log 2>&1 &
```

**使用screen:**
```bash
screen -S monitor
python server.py
# 按 Ctrl+A 然后 D 分离会话
```

## 📊 性能优化

1. **截图质量**：修改截图压缩率
2. **数据传输**：使用压缩减少流量
3. **并发连接**：支持多个客户端同时连接
4. **缓存机制**：缓存常用数据

## ❓ 常见问题

### Q: 无法连接到服务器？
A: 检查：
- 两台设备是否在同一网络
- IP地址是否正确
- 端口是否被占用
- 防火墙是否允许

### Q: 截图功能不可用？
A: 需要安装pillow：`pip install pillow`
   Android设备可能需要root权限

### Q: 权限不足？
A: Android设备需要授予存储权限
   某些功能需要root权限

### Q: 如何开机自启动？
A: 
- Android: 使用Tasker或类似工具
- Linux: 添加到systemd服务
- Windows: 添加到启动项

## 📄 许可证

本项目仅供学习和合法用途使用。使用者需自行承担法律责任。

## 🤝 贡献

欢迎提交问题和改进建议。

## ⚖️ 免责声明

本工具仅供合法用途，如：
- 管理自己的多台设备
- 家长监护未成年子女设备
- 企业管理公司设备

使用本工具进行非法监控是违法行为，开发者不承担任何责任。

