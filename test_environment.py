#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试脚本 - 用于验证环境配置
"""

import sys
import platform

def test_environment():
    """测试环境配置"""
    print("=" * 60)
    print("环境测试")
    print("=" * 60)
    
    # Python版本
    print(f"\n✓ Python版本: {sys.version}")
    print(f"✓ 平台: {platform.platform()}")
    
    # 测试依赖包
    print("\n检查依赖包:")
    
    packages = {
        'psutil': '系统信息监控',
        'PIL': '屏幕截图',
        'socket': '网络通信（内置）',
        'json': 'JSON处理（内置）',
        'threading': '多线程（内置）'
    }
    
    for package, description in packages.items():
        try:
            if package == 'PIL':
                __import__('PIL')
            else:
                __import__(package)
            print(f"  ✓ {package:<15} - {description}")
        except ImportError:
            print(f"  ✗ {package:<15} - {description} (未安装)")
    
    print("\n" + "=" * 60)
    print("测试完成")
    print("=" * 60)
    
    # 网络测试
    print("\n网络信息:")
    import socket
    hostname = socket.gethostname()
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(('8.8.8.8', 80))
        local_ip = s.getsockname()[0]
        s.close()
        print(f"  主机名: {hostname}")
        print(f"  本机IP: {local_ip}")
    except Exception as e:
        print(f"  无法获取IP: {e}")

if __name__ == '__main__':
    test_environment()
