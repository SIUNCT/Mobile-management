#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
图形化客户端 - 提供简单的GUI界面
需要安装: pip install tkinter (通常Python自带)
"""

try:
    import tkinter as tk
    from tkinter import scrolledtext, messagebox, filedialog
    import socket
    import json
    import threading
    import base64
    from datetime import datetime
except ImportError as e:
    print(f"缺少依赖: {e}")
    print("请安装: pip install tk")
    exit(1)

class MonitorGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("手机监控客户端")
        self.root.geometry("800x600")
        
        self.socket = None
        self.connected = False
        
        self.create_widgets()
    
    def create_widgets(self):
        """创建界面组件"""
        # 连接区域
        conn_frame = tk.Frame(self.root)
        conn_frame.pack(pady=10, padx=10, fill=tk.X)
        
        tk.Label(conn_frame, text="服务器IP:").pack(side=tk.LEFT)
        self.ip_entry = tk.Entry(conn_frame, width=20)
        self.ip_entry.pack(side=tk.LEFT, padx=5)
        self.ip_entry.insert(0, "192.168.1.100")
        
        tk.Label(conn_frame, text="端口:").pack(side=tk.LEFT)
        self.port_entry = tk.Entry(conn_frame, width=10)
        self.port_entry.pack(side=tk.LEFT, padx=5)
        self.port_entry.insert(0, "8888")
        
        self.connect_btn = tk.Button(conn_frame, text="连接", command=self.connect)
        self.connect_btn.pack(side=tk.LEFT, padx=5)
        
        self.disconnect_btn = tk.Button(conn_frame, text="断开", command=self.disconnect, state=tk.DISABLED)
        self.disconnect_btn.pack(side=tk.LEFT)
        
        self.status_label = tk.Label(conn_frame, text="未连接", fg="red")
        self.status_label.pack(side=tk.LEFT, padx=10)
        
        # 功能按钮区域
        btn_frame = tk.Frame(self.root)
        btn_frame.pack(pady=10, padx=10, fill=tk.X)
        
        buttons = [
            ("设备信息", self.get_info),
            ("截图", self.screenshot),
            ("进程列表", self.get_processes),
            ("文件浏览", self.browse_files),
            ("网络信息", self.get_network),
            ("清空输出", self.clear_output)
        ]
        
        for text, command in buttons:
            btn = tk.Button(btn_frame, text=text, command=command, width=12)
            btn.pack(side=tk.LEFT, padx=5)
        
        # 输出区域
        output_frame = tk.Frame(self.root)
        output_frame.pack(pady=10, padx=10, fill=tk.BOTH, expand=True)
        
        tk.Label(output_frame, text="输出:").pack(anchor=tk.W)
        
        self.output_text = scrolledtext.ScrolledText(output_frame, height=20, width=80)
        self.output_text.pack(fill=tk.BOTH, expand=True)
        
        # 命令输入区域
        cmd_frame = tk.Frame(self.root)
        cmd_frame.pack(pady=10, padx=10, fill=tk.X)
        
        tk.Label(cmd_frame, text="自定义命令:").pack(side=tk.LEFT)
        self.cmd_entry = tk.Entry(cmd_frame, width=50)
        self.cmd_entry.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        self.cmd_entry.bind('<Return>', lambda e: self.execute_custom_command())
        
        tk.Button(cmd_frame, text="执行", command=self.execute_custom_command).pack(side=tk.LEFT)
    
    def log(self, message):
        """输出日志"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.output_text.insert(tk.END, f"[{timestamp}] {message}\n")
        self.output_text.see(tk.END)
    
    def clear_output(self):
        """清空输出"""
        self.output_text.delete(1.0, tk.END)
    
    def connect(self):
        """连接到服务器"""
        host = self.ip_entry.get().strip()
        port = self.port_entry.get().strip()
        
        if not host or not port:
            messagebox.showerror("错误", "请输入IP地址和端口")
            return
        
        try:
            port = int(port)
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.settimeout(10)
            self.socket.connect((host, port))
            
            self.connected = True
            self.status_label.config(text="已连接", fg="green")
            self.connect_btn.config(state=tk.DISABLED)
            self.disconnect_btn.config(state=tk.NORMAL)
            self.log(f"✓ 已连接到 {host}:{port}")
            
            # 测试连接
            self.send_command('ping')
            
        except Exception as e:
            messagebox.showerror("连接失败", str(e))
            self.log(f"✗ 连接失败: {e}")
    
    def disconnect(self):
        """断开连接"""
        if self.socket:
            try:
                self.socket.close()
            except:
                pass
        
        self.connected = False
        self.socket = None
        self.status_label.config(text="未连接", fg="red")
        self.connect_btn.config(state=tk.NORMAL)
        self.disconnect_btn.config(state=tk.DISABLED)
        self.log("✓ 已断开连接")
    
    def send_command(self, command, params=None):
        """发送命令"""
        if not self.connected:
            messagebox.showwarning("警告", "请先连接到服务器")
            return None
        
        try:
            request = {
                'command': command,
                'params': params or {}
            }
            
            request_data = json.dumps(request, ensure_ascii=False)
            self.socket.sendall(request_data.encode('utf-8'))
            
            # 接收响应
            response_data = b''
            while True:
                chunk = self.socket.recv(4096)
                if not chunk:
                    break
                response_data += chunk
                if b'\n__END__\n' in response_data:
                    response_data = response_data.replace(b'\n__END__\n', b'')
                    break
            
            response = json.loads(response_data.decode('utf-8'))
            return response
            
        except Exception as e:
            self.log(f"✗ 命令执行失败: {e}")
            messagebox.showerror("错误", f"命令执行失败: {e}")
            return None
    
    def get_info(self):
        """获取设备信息"""
        self.log("正在获取设备信息...")
        response = self.send_command('info')
        
        if response and response.get('success'):
            data = response.get('data', {})
            self.log("\n设备信息:")
            self.log(f"  时间: {data.get('timestamp')}")
            self.log(f"  平台: {data.get('platform')}")
            self.log(f"  系统: {data.get('system')}")
            if 'cpu_percent' in data:
                self.log(f"  CPU: {data.get('cpu_percent')}%")
            if 'memory' in data:
                self.log(f"  内存: {data['memory'].get('percent')}%")
        else:
            self.log(f"✗ 获取失败: {response.get('error') if response else '无响应'}")
    
    def screenshot(self):
        """截图"""
        self.log("正在截取屏幕...")
        response = self.send_command('screenshot')
        
        if response and response.get('success'):
            filename = filedialog.asksaveasfilename(
                defaultextension=".png",
                filetypes=[("PNG图片", "*.png"), ("所有文件", "*.*")],
                initialfile=f"screenshot_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
            )
            
            if filename:
                img_data = response.get('data')
                img_bytes = base64.b64decode(img_data)
                
                with open(filename, 'wb') as f:
                    f.write(img_bytes)
                
                self.log(f"✓ 截图已保存: {filename}")
                messagebox.showinfo("成功", f"截图已保存到:\n{filename}")
        else:
            self.log(f"✗ 截图失败: {response.get('error') if response else '无响应'}")
    
    def get_processes(self):
        """获取进程列表"""
        self.log("正在获取进程列表...")
        response = self.send_command('processes')
        
        if response and response.get('success'):
            processes = response.get('processes', [])
            self.log(f"\n运行中的进程 (共{len(processes)}个):")
            self.log(f"{'PID':<8} {'名称':<30} {'CPU%':<8}")
            self.log("-" * 50)
            for proc in processes[:10]:  # 只显示前10个
                self.log(f"{proc.get('pid', 0):<8} {proc.get('name', 'N/A'):<30} {proc.get('cpu_percent', 0):<8.1f}")
        else:
            self.log(f"✗ 获取失败: {response.get('error') if response else '无响应'}")
    
    def browse_files(self):
        """浏览文件"""
        path = tk.simpledialog.askstring("浏览文件", "请输入路径:", 
                                         initialvalue="/sdcard/" if self.is_android() else "")
        if path:
            self.log(f"正在浏览: {path}")
            response = self.send_command('files', {'path': path})
            
            if response and response.get('success'):
                files = response.get('files', [])
                current_path = response.get('path')
                self.log(f"\n路径: {current_path}")
                self.log(f"{'类型':<8} {'名称':<40}")
                self.log("-" * 50)
                for item in files[:20]:  # 只显示前20个
                    file_type = '[DIR]' if item['is_dir'] else '[FILE]'
                    self.log(f"{file_type:<8} {item['name']:<40}")
            else:
                self.log(f"✗ 浏览失败: {response.get('error') if response else '无响应'}")
    
    def get_network(self):
        """获取网络信息"""
        self.log("正在获取网络信息...")
        response = self.send_command('network')
        
        if response and response.get('success'):
            interfaces = response.get('interfaces', {})
            self.log("\n网络接口:")
            for name, addrs in interfaces.items():
                self.log(f"  {name}:")
                for addr in addrs:
                    if 'address' in addr:
                        self.log(f"    {addr['address']}")
        else:
            self.log(f"✗ 获取失败: {response.get('error') if response else '无响应'}")
    
    def execute_custom_command(self):
        """执行自定义命令"""
        cmd = self.cmd_entry.get().strip()
        if not cmd:
            return
        
        self.log(f"执行命令: {cmd}")
        response = self.send_command('exec', {'command': cmd})
        
        if response and response.get('success'):
            self.log("\n输出:")
            self.log(response.get('stdout', '(无输出)'))
            if response.get('stderr'):
                self.log("\n错误:")
                self.log(response.get('stderr'))
        else:
            self.log(f"✗ 执行失败: {response.get('error') if response else '无响应'}")
        
        self.cmd_entry.delete(0, tk.END)
    
    def is_android(self):
        """判断服务端是否为Android"""
        # 简单判断，可以通过info命令获取更准确的信息
        return True

def main():
    root = tk.Tk()
    app = MonitorGUI(root)
    root.mainloop()

if __name__ == '__main__':
    main()
