#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
手机监控客户端 - 运行在控制端设备上
用于远程连接和控制备用手机
"""

import socket
import json
import base64
import os
import sys
from datetime import datetime

class PhoneMonitorClient:
    def __init__(self, host, port=8888):
        self.host = host
        self.port = port
        self.socket = None
        self.connected = False
        
    def connect(self):
        """连接到服务器"""
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.settimeout(10)
            self.socket.connect((self.host, self.port))
            self.connected = True
            print(f"✓ 已连接到 {self.host}:{self.port}")
            return True
        except Exception as e:
            print(f"✗ 连接失败: {e}")
            return False
    
    def disconnect(self):
        """断开连接"""
        if self.socket:
            try:
                self.socket.close()
            except:
                pass
        self.connected = False
        print("✓ 已断开连接")
    
    def send_command(self, command, params=None):
        """发送命令"""
        if not self.connected:
            print("✗ 未连接到服务器")
            return None
            
        try:
            request = {
                'command': command,
                'params': params or {}
            }
            
            # 发送请求
            request_data = json.dumps(request, ensure_ascii=False)
            self.socket.sendall(request_data.encode('utf-8'))
            
            # 接收响应
            response_data = b''
            while True:
                chunk = self.socket.recv(4096)
                if not chunk:
                    break
                response_data += chunk
                # 检查是否收到结束标记
                if b'\n__END__\n' in response_data:
                    response_data = response_data.replace(b'\n__END__\n', b'')
                    break
            
            # 解析响应
            response = json.loads(response_data.decode('utf-8'))
            return response
            
        except Exception as e:
            print(f"✗ 命令执行失败: {e}")
            return None
    
    def get_device_info(self):
        """获取设备信息"""
        print("\n📱 获取设备信息...")
        response = self.send_command('info')
        if response and response.get('success'):
            data = response.get('data', {})
            print("\n设备信息:")
            print(f"  时间: {data.get('timestamp')}")
            print(f"  平台: {data.get('platform')}")
            print(f"  系统: {data.get('system')}")
            print(f"  架构: {data.get('machine')}")
            if 'cpu_percent' in data:
                print(f"  CPU使用率: {data.get('cpu_percent')}%")
            if 'memory' in data:
                mem = data['memory']
                print(f"  内存使用: {mem.get('percent')}%")
            if 'disk' in data:
                disk = data['disk']
                print(f"  磁盘使用: {disk.get('percent')}%")
        else:
            print(f"✗ 获取失败: {response.get('error') if response else '无响应'}")
    
    def take_screenshot(self, save_path='screenshot.png'):
        """截取屏幕"""
        print("\n📸 正在截取屏幕...")
        response = self.send_command('screenshot')
        if response and response.get('success'):
            img_data = response.get('data')
            img_bytes = base64.b64decode(img_data)
            
            with open(save_path, 'wb') as f:
                f.write(img_bytes)
            
            print(f"✓ 截图已保存: {save_path}")
            print(f"  大小: {len(img_bytes)} 字节")
            print(f"  时间: {response.get('timestamp')}")
        else:
            print(f"✗ 截图失败: {response.get('error') if response else '无响应'}")
    
    def list_processes(self):
        """列出运行进程"""
        print("\n⚙️  获取运行进程...")
        response = self.send_command('processes')
        if response and response.get('success'):
            processes = response.get('processes', [])
            print(f"\n运行中的进程 (前20个):")
            print(f"{'PID':<8} {'名称':<30} {'CPU%':<8} {'内存%':<8}")
            print("-" * 60)
            for proc in processes:
                print(f"{proc.get('pid', 0):<8} {proc.get('name', 'N/A'):<30} "
                      f"{proc.get('cpu_percent', 0):<8.1f} {proc.get('memory_percent', 0):<8.1f}")
        else:
            print(f"✗ 获取失败: {response.get('error') if response else '无响应'}")
    
    def list_files(self, path=None):
        """列出文件"""
        print(f"\n📁 列出文件: {path or '默认目录'}")
        response = self.send_command('files', {'path': path})
        if response and response.get('success'):
            files = response.get('files', [])
            current_path = response.get('path')
            print(f"\n当前路径: {current_path}")
            print(f"\n{'类型':<6} {'名称':<40} {'大小':<15} {'修改时间'}")
            print("-" * 90)
            
            # 先显示目录
            for item in sorted(files, key=lambda x: (not x['is_dir'], x['name'])):
                file_type = '[DIR]' if item['is_dir'] else '[FILE]'
                size = '-' if item['is_dir'] else f"{item['size']:,} B"
                print(f"{file_type:<6} {item['name']:<40} {size:<15} {item.get('modified', 'N/A')}")
        else:
            print(f"✗ 获取失败: {response.get('error') if response else '无响应'}")
    
    def read_file(self, filepath, save_as=None):
        """读取文件"""
        print(f"\n📄 读取文件: {filepath}")
        response = self.send_command('read_file', {'filepath': filepath})
        if response and response.get('success'):
            content = response.get('content')
            file_type = response.get('type')
            file_size = response.get('size')
            
            print(f"✓ 文件读取成功")
            print(f"  类型: {file_type}")
            print(f"  大小: {file_size:,} 字节")
            
            if save_as:
                if file_type == 'text':
                    with open(save_as, 'w', encoding='utf-8') as f:
                        f.write(content)
                else:
                    with open(save_as, 'wb') as f:
                        f.write(base64.b64decode(content))
                print(f"✓ 已保存到: {save_as}")
            else:
                if file_type == 'text':
                    print("\n文件内容:")
                    print("-" * 60)
                    print(content[:1000])  # 只显示前1000字符
                    if len(content) > 1000:
                        print(f"\n... (还有 {len(content) - 1000} 字符)")
                else:
                    print("  (二进制文件，请使用 save_as 参数保存)")
        else:
            print(f"✗ 读取失败: {response.get('error') if response else '无响应'}")
    
    def execute_command(self, command):
        """执行系统命令"""
        print(f"\n💻 执行命令: {command}")
        response = self.send_command('exec', {'command': command})
        if response and response.get('success'):
            print("\n标准输出:")
            print(response.get('stdout', '(无输出)'))
            if response.get('stderr'):
                print("\n标准错误:")
                print(response.get('stderr'))
            print(f"\n返回码: {response.get('returncode')}")
        else:
            print(f"✗ 执行失败: {response.get('error') if response else '无响应'}")
    
    def get_network_info(self):
        """获取网络信息"""
        print("\n🌐 获取网络信息...")
        response = self.send_command('network')
        if response and response.get('success'):
            interfaces = response.get('interfaces', {})
            stats = response.get('stats', {})
            
            print("\n网络接口:")
            for name, addrs in interfaces.items():
                print(f"\n  {name}:")
                for addr in addrs:
                    if 'address' in addr:
                        print(f"    地址: {addr['address']}")
            
            print("\n网络统计:")
            print(f"  发送: {stats.get('bytes_sent', 0):,} 字节")
            print(f"  接收: {stats.get('bytes_recv', 0):,} 字节")
        else:
            print(f"✗ 获取失败: {response.get('error') if response else '无响应'}")
    
    def ping(self):
        """测试连接"""
        response = self.send_command('ping')
        if response and response.get('success'):
            print(f"✓ Pong! 服务器响应正常")
            print(f"  时间: {response.get('timestamp')}")
            return True
        else:
            print("✗ 服务器无响应")
            return False
    
    def interactive_mode(self):
        """交互模式"""
        print("\n" + "=" * 60)
        print("📱 手机监控客户端 - 交互模式")
        print("=" * 60)
        
        commands_help = """
可用命令:
  info          - 获取设备信息
  screenshot    - 截取屏幕
  processes     - 列出运行进程
  files [path]  - 列出文件
  read <file>   - 读取文件内容
  exec <cmd>    - 执行系统命令
  network       - 获取网络信息
  ping          - 测试连接
  help          - 显示帮助
  exit          - 退出
"""
        print(commands_help)
        
        while True:
            try:
                cmd_input = input("\n> ").strip()
                if not cmd_input:
                    continue
                
                parts = cmd_input.split(maxsplit=1)
                cmd = parts[0].lower()
                args = parts[1] if len(parts) > 1 else None
                
                if cmd == 'exit':
                    break
                elif cmd == 'help':
                    print(commands_help)
                elif cmd == 'info':
                    self.get_device_info()
                elif cmd == 'screenshot':
                    filename = args if args else f'screenshot_{datetime.now().strftime("%Y%m%d_%H%M%S")}.png'
                    self.take_screenshot(filename)
                elif cmd == 'processes':
                    self.list_processes()
                elif cmd == 'files':
                    self.list_files(args)
                elif cmd == 'read':
                    if args:
                        self.read_file(args)
                    else:
                        print("✗ 请指定文件路径")
                elif cmd == 'exec':
                    if args:
                        self.execute_command(args)
                    else:
                        print("✗ 请指定要执行的命令")
                elif cmd == 'network':
                    self.get_network_info()
                elif cmd == 'ping':
                    self.ping()
                else:
                    print(f"✗ 未知命令: {cmd}")
                    print("输入 'help' 查看可用命令")
                    
            except KeyboardInterrupt:
                print("\n使用 'exit' 命令退出")
            except Exception as e:
                print(f"✗ 错误: {e}")

def main():
    """主函数"""
    print("\n📱 手机监控客户端 v1.0\n")
    
    if len(sys.argv) < 2:
        print("用法: python client.py <服务器IP> [端口]")
        print("示例: python client.py 192.168.1.100 8888")
        sys.exit(1)
    
    host = sys.argv[1]
    port = int(sys.argv[2]) if len(sys.argv) > 2 else 8888
    
    client = PhoneMonitorClient(host, port)
    
    if client.connect():
        # 测试连接
        if client.ping():
            # 进入交互模式
            try:
                client.interactive_mode()
            except KeyboardInterrupt:
                print("\n\n[*] 收到中断信号")
            finally:
                client.disconnect()
    else:
        print("\n无法连接到服务器，请检查:")
        print("  1. 服务器是否已启动")
        print("  2. IP地址和端口是否正确")
        print("  3. 两台设备是否在同一网络")
        print("  4. 防火墙是否允许连接")

if __name__ == '__main__':
    main()
