#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
安装检查脚本 - 一键检查所有依赖和配置
"""

import sys
import subprocess
import platform

def check_python_version():
    """检查Python版本"""
    version = sys.version_info
    print(f"Python版本: {version.major}.{version.minor}.{version.micro}")
    if version.major >= 3 and version.minor >= 6:
        print("  ✓ Python版本符合要求 (3.6+)")
        return True
    else:
        print("  ✗ Python版本过低，需要3.6或更高版本")
        return False

def check_package(package_name, import_name=None):
    """检查包是否已安装"""
    if import_name is None:
        import_name = package_name
    
    try:
        __import__(import_name)
        print(f"  ✓ {package_name} 已安装")
        return True
    except ImportError:
        print(f"  ✗ {package_name} 未安装")
        return False

def install_packages():
    """安装缺失的包"""
    print("\n是否自动安装缺失的包？(y/n): ", end='')
    choice = input().strip().lower()
    
    if choice == 'y':
        print("\n正在安装依赖包...")
        try:
            subprocess.check_call([sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'])
            print("\n✓ 依赖包安装完成！")
            return True
        except subprocess.CalledProcessError:
            print("\n✗ 安装失败，请手动执行: pip install -r requirements.txt")
            return False
    return False

def check_network():
    """检查网络配置"""
    import socket
    try:
        hostname = socket.gethostname()
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(('8.8.8.8', 80))
        local_ip = s.getsockname()[0]
        s.close()
        
        print(f"  主机名: {hostname}")
        print(f"  本机IP: {local_ip}")
        print("  ✓ 网络配置正常")
        return True
    except Exception as e:
        print(f"  ✗ 网络配置异常: {e}")
        return False

def main():
    print("=" * 60)
    print("手机监控系统 - 安装检查")
    print("=" * 60)
    
    all_ok = True
    
    # 检查Python版本
    print("\n[1] 检查Python版本")
    if not check_python_version():
        all_ok = False
    
    # 检查系统信息
    print("\n[2] 系统信息")
    print(f"  操作系统: {platform.system()}")
    print(f"  平台: {platform.platform()}")
    print(f"  架构: {platform.machine()}")
    
    # 检查必需的包
    print("\n[3] 检查依赖包")
    packages = {
        'psutil': 'psutil',
        'Pillow': 'PIL',
    }
    
    missing_packages = []
    for pkg_name, import_name in packages.items():
        if not check_package(pkg_name, import_name):
            missing_packages.append(pkg_name)
            all_ok = False
    
    # 检查内置模块
    print("\n[4] 检查内置模块")
    builtin_modules = ['socket', 'json', 'threading', 'base64']
    for module in builtin_modules:
        check_package(module)
    
    # 检查网络
    print("\n[5] 检查网络配置")
    check_network()
    
    # 总结
    print("\n" + "=" * 60)
    if all_ok:
        print("✓ 所有检查通过！可以开始使用了")
        print("\n下一步：")
        print("  1. 在服务端设备运行: python server.py")
        print("  2. 在客户端设备运行: python client.py <服务端IP>")
    else:
        print("✗ 发现问题，需要处理")
        if missing_packages:
            print(f"\n缺失的包: {', '.join(missing_packages)}")
            install_packages()
    
    print("=" * 60)

if __name__ == '__main__':
    main()
