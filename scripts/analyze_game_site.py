#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
游戏网站分析工具 - 帮助确定新网站应该添加到哪个配置
"""

import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse, urljoin
import sys
import re

def analyze_game_site(url):
    """分析游戏网站类型"""
    print(f"🔍 分析网站: {url}")
    print("=" * 50)
    
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        parsed = urlparse(url)
        
        # 分析网站类型
        site_type = determine_site_type(soup, url)
        
        if site_type == 'game_platform':
            analyze_as_platform(soup, url)
        elif site_type == 'game_host':
            analyze_as_host(soup, url)
        else:
            print("❓ 无法确定网站类型，请手动检查")
            
    except Exception as e:
        print(f"❌ 分析失败: {e}")

def determine_site_type(soup, url):
    """判断网站类型"""
    # 检查是否是游戏平台（有游戏列表）
    game_list_indicators = [
        '.game', '.game-item', '.game-card', '.game-cell',
        '[class*="game"]', '[id*="game"]',
        '.title', '.game-title', '.name'
    ]
    
    game_elements = 0
    for selector in game_list_indicators:
        elements = soup.select(selector)
        if len(elements) > 5:  # 如果找到多个游戏元素
            game_elements += len(elements)
    
    # 检查是否是游戏托管域名
    if any(keyword in url.lower() for keyword in ['cdn', 'assets', 'static', 'embed', 'games.']):
        return 'game_host'
    
    # 检查页面内容
    text = soup.get_text().lower()
    if game_elements > 10 and any(keyword in text for keyword in ['games', 'play', 'free']):
        return 'game_platform'
    elif any(keyword in url.lower() for keyword in ['embed', 'iframe', '.js', '.html']):
        return 'game_host'
    
    return 'unknown'

def analyze_as_platform(soup, url):
    """作为游戏平台分析"""
    print("🎮 检测到：游戏平台网站")
    print("📍 应添加到：PREMIUM_GAME_SITES")
    print()
    
    parsed = urlparse(url)
    
    # 寻找可能的游戏选择器
    potential_selectors = [
        '.game', '.game-item', '.game-card', '.game-cell', '.game-thumbnail',
        '[class*="game"]', '.item', '.card', '.thumbnail'
    ]
    
    print("🔍 可能的游戏选择器:")
    for selector in potential_selectors:
        elements = soup.select(selector)
        if 3 <= len(elements) <= 50:  # 合理的游戏数量
            print(f"  ✅ '{selector}' ({len(elements)} 个元素)")
        elif len(elements) > 0:
            print(f"  ⚠️ '{selector}' ({len(elements)} 个元素 - 可能太多/太少)")
    
    # 寻找标题选择器
    print("\n🏷️ 可能的标题选择器:")
    title_selectors = ['.title', '.name', '.game-title', '.game-name', 'h1', 'h2', 'h3', 'a']
    for selector in title_selectors:
        elements = soup.select(selector)
        if len(elements) > 0:
            sample_text = elements[0].get_text(strip=True)[:30]
            if sample_text and len(sample_text) > 2:
                print(f"  ✅ '{selector}' (示例: '{sample_text}')")
    
    # 生成配置示例
    print(f"\n📝 建议的配置:")
    print(f"{{")
    print(f"    'name': '{parsed.netloc}',")
    print(f"    'base_url': '{parsed.scheme}://{parsed.netloc}',")
    print(f"    'search_url': '{url}',")
    print(f"    'game_selector': '.game',  # 请根据上面的分析调整")
    print(f"    'title_selector': '.title',  # 请根据上面的分析调整")
    print(f"    'priority': 3")
    print(f"}}")

def analyze_as_host(soup, url):
    """作为游戏托管域名分析"""
    print("🗄️ 检测到：游戏托管域名")
    print("📍 应添加到：EMBEDDABLE_DOMAINS")
    print()
    
    parsed = urlparse(url)
    domain = parsed.netloc
    
    # 检查iframe或游戏内容
    iframes = soup.select('iframe')
    scripts = soup.select('script[src]')
    
    print(f"🔍 域名分析:")
    print(f"  域名: {domain}")
    print(f"  路径: {parsed.path}")
    
    if iframes:
        print(f"  ✅ 包含 {len(iframes)} 个iframe")
    
    if scripts:
        print(f"  ✅ 包含 {len(scripts)} 个外部脚本")
    
    # 检查是否是游戏相关的路径
    game_path_patterns = ['/game/', '/play/', '/embed/', '/html5/', '/games/']
    matching_patterns = [pattern for pattern in game_path_patterns if pattern in parsed.path]
    
    if matching_patterns:
        print(f"  ✅ 包含游戏相关路径: {matching_patterns}")
    
    print(f"\n📝 建议添加到 EMBEDDABLE_DOMAINS:")
    print(f"'{domain}',")
    
    # 如果有特定路径，也提供路径版本
    if parsed.path and len(parsed.path) > 1:
        print(f"# 或者更具体的路径:")
        print(f"'{domain}{parsed.path}',")

def main():
    """主函数"""
    if len(sys.argv) != 2:
        print("用法: python analyze_game_site.py <网站URL>")
        print("示例: python analyze_game_site.py https://example.com/games")
        return
    
    url = sys.argv[1]
    if not url.startswith(('http://', 'https://')):
        url = 'https://' + url
    
    analyze_game_site(url)

if __name__ == '__main__':
    main() 