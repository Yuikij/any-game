#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简单的代理设置工具 - 类似Java的全局代理
"""

import os
import sys
import requests

def set_proxy(host='127.0.0.1', port='7890'):
    """设置全局代理"""
    proxy_url = f"http://{host}:{port}"
    
    print(f"🌐 设置代理: {host}:{port}")
    
    # 设置环境变量（对当前进程及子进程生效）
    os.environ['HTTP_PROXY'] = proxy_url
    os.environ['HTTPS_PROXY'] = proxy_url
    os.environ['http_proxy'] = proxy_url
    os.environ['https_proxy'] = proxy_url
    
    # 测试代理
    try:
        print("🔍 测试代理连接...")
        response = requests.get('https://httpbin.org/ip', 
                               proxies={'http': proxy_url, 'https': proxy_url}, 
                               timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ 代理测试成功！")
            print(f"   原始IP: {data.get('origin', 'Unknown')}")
            print(f"   代理URL: {proxy_url}")
            return True
        else:
            print(f"❌ 代理测试失败: HTTP {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ 代理连接失败: {e}")
        return False

def clear_proxy():
    """清除代理设置"""
    print("🧹 清除代理设置...")
    
    proxy_vars = ['HTTP_PROXY', 'HTTPS_PROXY', 'http_proxy', 'https_proxy']
    for var in proxy_vars:
        if var in os.environ:
            del os.environ[var]
    
    print("✅ 代理已清除")

def main():
    """主函数"""
    if len(sys.argv) < 2:
        print("用法:")
        print("  python set_proxy.py set [host] [port]  # 设置代理（默认127.0.0.1:7890）")
        print("  python set_proxy.py clear              # 清除代理")
        print("  python set_proxy.py test               # 测试当前代理")
        return
    
    command = sys.argv[1].lower()
    
    if command == 'set':
        host = sys.argv[2] if len(sys.argv) > 2 else '127.0.0.1'
        port = sys.argv[3] if len(sys.argv) > 3 else '7890'
        set_proxy(host, port)
        
    elif command == 'clear':
        clear_proxy()
        
    elif command == 'test':
        proxy_host = os.environ.get('HTTP_PROXY', '未设置')
        print(f"当前代理: {proxy_host}")
        
        if proxy_host != '未设置':
            try:
                response = requests.get('https://httpbin.org/ip', timeout=10)
                data = response.json()
                print(f"当前IP: {data.get('origin', 'Unknown')}")
            except Exception as e:
                print(f"网络测试失败: {e}")
        
    else:
        print(f"未知命令: {command}")

if __name__ == '__main__':
    main() 