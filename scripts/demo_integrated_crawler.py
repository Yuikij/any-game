#!/usr/bin/env python3
"""
集成游戏爬虫演示脚本
展示所有功能的使用方法和效果
"""

import os
import sys
import time
import subprocess
from datetime import datetime

def print_banner():
    """打印横幅"""
    print("=" * 60)
    print("🎮 集成游戏爬虫演示 🎮")
    print("=" * 60)
    print()

def print_section(title: str):
    """打印章节标题"""
    print(f"\n📌 {title}")
    print("-" * 40)

def run_command(cmd: str, description: str):
    """运行命令并显示结果"""
    print(f"🚀 {description}")
    print(f"命令: {cmd}")
    print()
    
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, encoding='utf-8')
        
        if result.stdout:
            print("✅ 输出:")
            print(result.stdout)
        
        if result.stderr:
            print("⚠️ 错误:")
            print(result.stderr)
        
        if result.returncode == 0:
            print("✅ 执行成功")
        else:
            print(f"❌ 执行失败，退出码: {result.returncode}")
            
    except Exception as e:
        print(f"❌ 执行异常: {e}")
    
    print("\n" + "="*40)
    input("按回车键继续...")

def check_dependencies():
    """检查依赖"""
    print_section("依赖检查")
    
    dependencies = [
        ("requests", "HTTP请求库"),
        ("beautifulsoup4", "HTML解析库"),
        ("lxml", "XML解析库"),
        ("pillow", "图像处理库"),
        ("aiohttp", "异步HTTP库")
    ]
    
    for package, desc in dependencies:
        try:
            __import__(package.replace('-', '_'))
            print(f"✅ {package} ({desc}) - 已安装")
        except ImportError:
            print(f"❌ {package} ({desc}) - 未安装")
            print(f"   安装命令: pip install {package}")
    
    print("\n如果有未安装的库，请先安装:")
    print("pip install requests beautifulsoup4 lxml pillow aiohttp")

def show_help():
    """显示帮助信息"""
    print_section("帮助信息")
    cmd = "python scripts/integrated_game_crawler.py --help"
    run_command(cmd, "显示集成爬虫帮助信息")

def demo_quick_mode():
    """演示快速模式"""
    print_section("快速模式演示")
    print("快速模式特点:")
    print("- 主要从itch.io平台爬取")
    print("- 速度最快")
    print("- 适合测试和小量爬取")
    print()
    
    cmd = "python scripts/integrated_game_crawler.py --mode quick --target 3"
    run_command(cmd, "快速模式爬取3个游戏")

def demo_thumbnail_generation():
    """演示缩略图生成"""
    print_section("缩略图生成演示")
    print("缩略图功能:")
    print("- 8种颜色主题")
    print("- 4种几何图案")
    print("- 自动文字布局")
    print("- 300x200像素")
    print()
    
    cmd = "python scripts/generate_thumbnails.py --count 10"
    run_command(cmd, "生成10个示例缩略图")

def demo_statistics():
    """演示统计功能"""
    print_section("统计信息演示")
    
    cmd = "python scripts/check_stats.py"
    run_command(cmd, "查看当前游戏统计")

def show_configuration():
    """显示配置说明"""
    print_section("配置文件说明")
    
    print("📁 代理配置 (config/proxies.txt):")
    print("```")
    print("http://127.0.0.1:8080")
    print("http://username:password@proxy.example.com:8888")
    print("```")
    print()
    
    print("📁 API密钥配置 (config/api_keys.json):")
    print("```json")
    print('{')
    print('  "serp_api_key": "your_serpapi_key_here"')
    print('}')
    print("```")
    print()
    
    print("🔧 使用配置:")
    print("- 代理: --use-proxy")
    print("- API搜索: --api-search")
    print()

def show_examples():
    """显示使用示例"""
    print_section("使用示例")
    
    examples = [
        ("基础使用", "python scripts/integrated_game_crawler.py"),
        ("快速模式", "python scripts/integrated_game_crawler.py --mode quick --target 20"),
        ("完整模式", "python scripts/integrated_game_crawler.py --mode full --target 50"),
        ("使用代理", "python scripts/integrated_game_crawler.py --use-proxy"),
        ("API搜索", "python scripts/integrated_game_crawler.py --api-search"),
        ("指定平台", "python scripts/integrated_game_crawler.py --platforms itch.io"),
        ("自定义延迟", "python scripts/integrated_game_crawler.py --delay 1.0-2.0"),
        ("多线程", "python scripts/integrated_game_crawler.py --workers 5"),
        ("组合参数", "python scripts/integrated_game_crawler.py --mode full --use-proxy --api-search --workers 5")
    ]
    
    for name, cmd in examples:
        print(f"📖 {name}:")
        print(f"   {cmd}")
        print()

def show_performance():
    """显示性能信息"""
    print_section("性能指标")
    
    print("📈 标准配置下的性能:")
    print("- 速度: 每分钟约10-20个游戏")
    print("- 成功率: 80-90%")
    print("- 内存使用: 约50-100MB")
    print("- 网络流量: 每个游戏约50-200KB")
    print()
    
    print("⚡ 性能优化建议:")
    print("- 增加并发数: --workers 5")
    print("- 减少延迟: --delay 0.3-0.8")
    print("- 选择稳定平台: --platforms itch.io")
    print("- 使用代理: --use-proxy")
    print()

def show_troubleshooting():
    """显示故障排除"""
    print_section("故障排除")
    
    print("🚨 常见问题:")
    print()
    print("1. 没有找到游戏:")
    print("   - 检查网络连接")
    print("   - 尝试使用代理")
    print("   - 降低并发数")
    print()
    print("2. 缩略图生成失败:")
    print("   - 确保安装了Pillow库")
    print("   - 检查目录权限")
    print("   - 查看详细错误日志")
    print()
    print("3. API搜索无结果:")
    print("   - 检查API密钥配置")
    print("   - 确认API额度充足")
    print("   - 验证网络连接")
    print()

def main():
    """主函数"""
    print_banner()
    
    print("欢迎使用集成游戏爬虫演示！")
    print("本演示将展示所有功能和使用方法。")
    print()
    
    while True:
        print("\n🎯 请选择演示内容:")
        print("1. 检查依赖")
        print("2. 显示帮助信息")
        print("3. 演示快速模式")
        print("4. 演示缩略图生成")
        print("5. 查看统计信息")
        print("6. 配置文件说明")
        print("7. 使用示例")
        print("8. 性能指标")
        print("9. 故障排除")
        print("0. 退出")
        
        choice = input("\n请输入选择 (0-9): ").strip()
        
        if choice == "1":
            check_dependencies()
        elif choice == "2":
            show_help()
        elif choice == "3":
            demo_quick_mode()
        elif choice == "4":
            demo_thumbnail_generation()
        elif choice == "5":
            demo_statistics()
        elif choice == "6":
            show_configuration()
        elif choice == "7":
            show_examples()
        elif choice == "8":
            show_performance()
        elif choice == "9":
            show_troubleshooting()
        elif choice == "0":
            print("\n👋 感谢使用集成游戏爬虫演示！")
            break
        else:
            print("❌ 无效选择，请输入0-9之间的数字。")

if __name__ == "__main__":
    main() 