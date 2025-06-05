#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
API配置设置脚本
用于配置SerpAPI和Google Custom Search API密钥
"""

import os
import sys

def setup_api_config():
    """交互式配置API"""
    print("🔧 API配置设置")
    print("=" * 50)
    print()
    
    print("📋 可选配置的API服务：")
    print("1. SerpAPI (推荐) - https://serpapi.com/")
    print("2. Google Custom Search API - https://developers.google.com/custom-search/v1/introduction")
    print()
    print("💡 注意：即使不配置API，游戏管理器仍然可以正常工作（使用基础爬虫）")
    print()
    
    # 读取现有环境变量
    current_serpapi = os.getenv('SERPAPI_KEY', '')
    current_google_key = os.getenv('GOOGLE_API_KEY', '')
    current_google_cx = os.getenv('GOOGLE_CX', '')
    
    if current_serpapi:
        print(f"✅ 当前SerpAPI Key: {current_serpapi[:10]}...")
    if current_google_key:
        print(f"✅ 当前Google API Key: {current_google_key[:10]}...")
    if current_google_cx:
        print(f"✅ 当前Google CX: {current_google_cx}")
    
    print()
    
    # 配置SerpAPI
    print("🔍 配置SerpAPI (推荐)")
    print("获取方法：")
    print("1. 访问 https://serpapi.com/")
    print("2. 注册免费账户（每月100次免费搜索）")
    print("3. 在Dashboard中找到API Key")
    print()
    
    serpapi_key = input(f"请输入SerpAPI Key（留空跳过，当前: {current_serpapi[:10] + '...' if current_serpapi else '未配置'}）: ").strip()
    if not serpapi_key:
        serpapi_key = current_serpapi
    
    print()
    
    # 配置Google Custom Search
    print("🌐 配置Google Custom Search API")
    print("获取方法：")
    print("1. 访问 https://developers.google.com/custom-search/v1/introduction")
    print("2. 创建项目并启用Custom Search API")
    print("3. 创建自定义搜索引擎：https://cse.google.com/")
    print("4. 获取API Key和搜索引擎ID (CX)")
    print()
    
    google_key = input(f"请输入Google API Key（留空跳过，当前: {current_google_key[:10] + '...' if current_google_key else '未配置'}）: ").strip()
    if not google_key:
        google_key = current_google_key
    
    google_cx = input(f"请输入Google搜索引擎ID (CX)（留空跳过，当前: {current_google_cx or '未配置'}）: ").strip()
    if not google_cx:
        google_cx = current_google_cx
    
    print()
    
    # 设置方式选择
    print("💾 选择配置保存方式：")
    print("1. 临时设置（仅当前会话有效）")
    print("2. 创建批处理文件（Windows推荐）")
    print("3. 显示手动设置命令")
    
    choice = input("请选择 (1-3): ").strip()
    
    if choice == '1':
        # 临时设置环境变量
        if serpapi_key:
            os.environ['SERPAPI_KEY'] = serpapi_key
            print(f"✅ 已设置SERPAPI_KEY: {serpapi_key[:10]}...")
        
        if google_key:
            os.environ['GOOGLE_API_KEY'] = google_key
            print(f"✅ 已设置GOOGLE_API_KEY: {google_key[:10]}...")
        
        if google_cx:
            os.environ['GOOGLE_CX'] = google_cx
            print(f"✅ 已设置GOOGLE_CX: {google_cx}")
        
        print("\n🎯 临时设置完成！现在可以运行游戏管理器了：")
        print("python scripts/game_manager.py --action crawl")
    
    elif choice == '2':
        # 创建批处理文件
        batch_content = "@echo off\n"
        batch_content += "echo 🔧 设置API环境变量...\n"
        
        if serpapi_key:
            batch_content += f"set SERPAPI_KEY={serpapi_key}\n"
            batch_content += f"echo ✅ SERPAPI_KEY: {serpapi_key[:10]}...\n"
        
        if google_key:
            batch_content += f"set GOOGLE_API_KEY={google_key}\n"
            batch_content += f"echo ✅ GOOGLE_API_KEY: {google_key[:10]}...\n"
        
        if google_cx:
            batch_content += f"set GOOGLE_CX={google_cx}\n"
            batch_content += f"echo ✅ GOOGLE_CX: {google_cx}\n"
        
        batch_content += "echo.\n"
        batch_content += "echo 🚀 运行游戏管理器...\n"
        batch_content += "python scripts/game_manager.py --action crawl\n"
        batch_content += "pause\n"
        
        batch_file = "run_with_api.bat"
        with open(batch_file, 'w', encoding='utf-8') as f:
            f.write(batch_content)
        
        print(f"\n✅ 已创建批处理文件: {batch_file}")
        print("🎯 使用方法：双击运行 run_with_api.bat")
    
    elif choice == '3':
        # 显示手动设置命令
        print("\n📋 手动设置命令：")
        print("\n--- Windows (PowerShell) ---")
        if serpapi_key:
            print(f"$env:SERPAPI_KEY='{serpapi_key}'")
        if google_key:
            print(f"$env:GOOGLE_API_KEY='{google_key}'")
        if google_cx:
            print(f"$env:GOOGLE_CX='{google_cx}'")
        
        print("\n--- Windows (CMD) ---")
        if serpapi_key:
            print(f"set SERPAPI_KEY={serpapi_key}")
        if google_key:
            print(f"set GOOGLE_API_KEY={google_key}")
        if google_cx:
            print(f"set GOOGLE_CX={google_cx}")
        
        print("\n--- Linux/Mac ---")
        if serpapi_key:
            print(f"export SERPAPI_KEY='{serpapi_key}'")
        if google_key:
            print(f"export GOOGLE_API_KEY='{google_key}'")
        if google_cx:
            print(f"export GOOGLE_CX='{google_cx}'")
        
        print("\n🎯 设置后运行：")
        print("python scripts/game_manager.py --action crawl")
    
    print("\n" + "=" * 50)
    print("🎉 API配置完成！")
    
    if serpapi_key or (google_key and google_cx):
        print("✅ 现在可以使用增强的API搜索功能了")
    else:
        print("⚠️ 未配置API，将使用基础爬虫功能")

def test_api_config():
    """测试API配置"""
    print("🧪 测试API配置")
    print("=" * 30)
    
    serpapi_key = os.getenv('SERPAPI_KEY')
    google_key = os.getenv('GOOGLE_API_KEY')
    google_cx = os.getenv('GOOGLE_CX')
    
    if serpapi_key:
        print(f"✅ SerpAPI Key: {serpapi_key[:10]}...")
        try:
            import requests
            response = requests.get(f"https://serpapi.com/search?q=test&api_key={serpapi_key}&engine=google&num=1", timeout=10)
            if response.status_code == 200:
                print("✅ SerpAPI连接成功")
            else:
                print(f"❌ SerpAPI连接失败: {response.status_code}")
        except Exception as e:
            print(f"❌ SerpAPI测试失败: {e}")
    else:
        print("⚠️ SerpAPI未配置")
    
    if google_key and google_cx:
        print(f"✅ Google API Key: {google_key[:10]}...")
        print(f"✅ Google CX: {google_cx}")
        try:
            import requests
            params = {'key': google_key, 'cx': google_cx, 'q': 'test', 'num': 1}
            response = requests.get('https://www.googleapis.com/customsearch/v1', params=params, timeout=10)
            if response.status_code == 200:
                print("✅ Google Custom Search API连接成功")
            else:
                print(f"❌ Google Custom Search API连接失败: {response.status_code}")
        except Exception as e:
            print(f"❌ Google Custom Search API测试失败: {e}")
    else:
        print("⚠️ Google Custom Search API未配置")

def main():
    """主函数"""
    if len(sys.argv) > 1 and sys.argv[1] == 'test':
        test_api_config()
    else:
        setup_api_config()

if __name__ == '__main__':
    main() 