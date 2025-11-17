# 快速演示指南

## 场景：在同一WiFi下监控备用手机

### 准备工作

**设备A（被监控的备用手机）：**
- 安装Python 3.6+
- 连接到WiFi网络

**设备B（控制端）：**
- 安装Python 3.6+
- 连接到同一WiFi网络

---

## 详细步骤

### 1. 在设备A（备用手机）上操作

#### 如果是Android手机：

```bash
# 1. 安装Termux（从F-Droid下载）
# 2. 打开Termux，执行以下命令：

pkg update
pkg install python
pip install psutil

# 3. 传输server.py到手机
# 4. 在Termux中运行
cd /sdcard/Download
python server.py
```

#### 如果是电脑：

```bash
cd phone_monitor_project
pip install -r requirements.txt
python server.py
```

**重要：记下显示的IP地址！**
例如：192.168.1.100:8888

---

### 2. 在设备B（控制端）上操作

```bash
cd phone_monitor_project
python client.py 192.168.1.100
```

---

### 3. 开始使用

连接成功后，输入命令：

```bash
# 查看设备信息
> info

# 截取屏幕
> screenshot

# 查看运行进程
> processes

# 浏览文件
> files /sdcard/

# 读取文件
> read /sdcard/test.txt

# 执行命令
> exec ls -la

# 退出
> exit
```

---

## 常见问题

### 无法连接？

检查：
- 两台设备是否在同一网络
- IP地址是否正确
- 防火墙是否允许端口8888

### 截图失败？

安装依赖：
```bash
pip install pillow
```

---

## 高级技巧

### 后台运行服务端

Linux/Android:
```bash
nohup python server.py > server.log 2>&1 &
```

### 修改端口

```bash
python server.py 9999
python client.py 192.168.1.100 9999
```

---

## 安全建议

1. 仅在可信网络使用
2. 不要在公共WiFi使用
3. 启用密码保护（修改config.ini）
4. 定期检查日志文件

---

## Android特别说明

### Termux安装
- 从F-Droid下载（不要用Google Play）
- GitHub: https://github.com/termux/termux-app

### 常用路径
- 内部存储：/sdcard/
- 下载目录：/sdcard/Download/
- 照片目录：/sdcard/DCIM/Camera/

---

## 法律声明

请确保：
- 监控自己的设备
- 获得设备所有者授权
- 符合当地法律法规
- 不要非法监控他人

---

祝使用愉快！
