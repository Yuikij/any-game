#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
配置查看工具
显示当前游戏管理器的配置状态
"""

from config import Config

def main():
    """显示配置状态"""
    print("=" * 60)
    print("🔧 游戏管理器配置状态")
    print("=" * 60)
    
    Config.print_status()
    
    print("\n📁 路径配置:")
    print(f"  项目根目录: {Config.PROJECT_ROOT}")
    print(f"  游戏数据文件: {Config.GAMES_DATA_FILE}")
    print(f"  本地游戏目录: {Config.LOCAL_GAMES_DIR}")
    print(f"  缩略图目录: {Config.THUMBNAILS_DIR}")
    
    print("\n🎯 爬虫配置:")
    print(f"  延迟范围: {Config.CRAWL_DELAY_MIN}s - {Config.CRAWL_DELAY_MAX}s")
    print(f"  请求超时: {Config.REQUEST_TIMEOUT}s")
    print(f"  重试次数: {Config.RETRY_ATTEMPTS}")
    print(f"  智能评分阈值: {Config.GAME_URL_SCORE_THRESHOLD}")
    
    print("\n🚦 平台特定延迟配置:")
    for platform, (min_delay, max_delay) in Config.PLATFORM_DELAYS.items():
        if platform == 'default':
            print(f"  📋 {platform}: {min_delay}s - {max_delay}s （其他平台默认）")
        else:
            status = "🟢" if min_delay >= 3.0 else "🟡" if min_delay >= 2.0 else "🔴"
            print(f"  {status} {platform}: {min_delay}s - {max_delay}s")
    
    print("\n💡 配置方法:")
    print("  1. 直接编辑 scripts/config.py 文件")
    print("  2. 设置环境变量 (export USE_PROXY=true)")
    print("  3. 使用命令行参数 (--use-proxy --strict-whitelist)")
    
    print("\n📖 更多信息:")
    print("  详细配置说明: scripts/WHITELIST_MODES.md")
    print("  选择器检测说明: scripts/SELECTOR_DETECTION.md")
    
    print("=" * 60)

if __name__ == '__main__':
    main() 