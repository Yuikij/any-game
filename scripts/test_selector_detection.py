#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
选择器检测测试工具
用于测试新游戏平台的自动选择器检测功能
"""

import requests
from bs4 import BeautifulSoup
import json
from urllib.parse import urljoin, urlparse
import logging

# 导入共享配置
from config import Config, get_proxy_settings

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_selector_detection(url: str, site_name: str = None):
    """测试指定网站的选择器检测"""
    if not site_name:
        parsed = urlparse(url)
        site_name = parsed.netloc
    
    logger.info(f"🔍 测试网站: {site_name}")
    logger.info(f"🌐 URL: {url}")
    
    try:
        # 导入GameManager（延迟导入避免循环依赖）
        from game_manager import GameManager, get_random_headers
        
        # 创建GameManager实例
        manager = GameManager()
        
        # 获取页面内容
        headers = get_random_headers()
        proxies = get_proxy_settings()
        response = requests.get(url, headers=headers, proxies=proxies, timeout=Config.REQUEST_TIMEOUT)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        logger.info(f"✅ 页面加载成功，大小: {len(response.text)} 字符")
        
        # 执行选择器检测
        detected_selectors = manager._detect_game_selectors(soup, site_name)
        
        if detected_selectors:
            game_selector = detected_selectors.get('game_selector')
            title_selector = detected_selectors.get('title_selector')
            
            logger.info("🎯 检测结果:")
            logger.info(f"  游戏容器选择器: {game_selector}")
            logger.info(f"  标题选择器: {title_selector}")
            
            # 验证检测结果
            logger.info("🧪 验证检测结果...")
            game_elements = soup.select(game_selector)
            logger.info(f"  找到 {len(game_elements)} 个游戏元素")
            
            # 显示前几个游戏的标题
            for i, element in enumerate(game_elements[:5]):
                try:
                    title_elem = element.select_one(title_selector)
                    if title_elem:
                        title = title_elem.get_text(strip=True)
                        link_elem = element.select_one('a[href]') or (element if element.name == 'a' else None)
                        game_url = ""
                        if link_elem and link_elem.get('href'):
                            game_url = urljoin(url, link_elem['href'])
                        
                        logger.info(f"  游戏 {i+1}: {title}")
                        if game_url:
                            logger.info(f"    链接: {game_url}")
                except Exception as e:
                    logger.warning(f"  游戏 {i+1}: 解析失败 - {e}")
            
            # 生成配置建议
            config_suggestion = {
                'name': site_name,
                'base_url': f"{urlparse(url).scheme}://{urlparse(url).netloc}",
                'search_url': url,
                'game_selector': game_selector,
                'title_selector': title_selector,
                'priority': 5
            }
            
            logger.info("📋 建议的配置:")
            print(json.dumps(config_suggestion, indent=2, ensure_ascii=False))
            
        else:
            logger.error("❌ 未能检测到合适的选择器")
            logger.info("🔍 手动分析页面结构...")
            
            # 提供一些手动分析的信息
            analyze_page_structure(soup, url)
    
    except Exception as e:
        logger.error(f"❌ 测试失败: {e}")

def analyze_page_structure(soup: BeautifulSoup, url: str):
    """手动分析页面结构，提供调试信息"""
    logger.info("📊 页面结构分析:")
    
    # 分析常见的容器类名
    common_classes = {}
    for element in soup.find_all(class_=True):
        for class_name in element.get('class', []):
            if any(keyword in class_name.lower() for keyword in ['game', 'item', 'card', 'entry', 'product']):
                common_classes[class_name] = common_classes.get(class_name, 0) + 1
    
    if common_classes:
        logger.info("  常见的游戏相关class:")
        for class_name, count in sorted(common_classes.items(), key=lambda x: x[1], reverse=True)[:10]:
            logger.info(f"    .{class_name}: {count} 个元素")
    
    # 分析链接模式
    links = soup.find_all('a', href=True)
    game_links = []
    for link in links[:20]:  # 只分析前20个链接
        href = link.get('href', '')
        text = link.get_text(strip=True)
        if text and len(text) > 2 and len(text) < 100:
            full_url = urljoin(url, href)
            game_links.append((text, full_url))
    
    if game_links:
        logger.info("  可能的游戏链接:")
        for text, link_url in game_links[:5]:
            logger.info(f"    {text}: {link_url}")

def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description='测试游戏网站的选择器自动检测')
    parser.add_argument('url', help='要测试的网站URL')
    parser.add_argument('--name', help='网站名称（可选）')
    
    args = parser.parse_args()
    
    test_selector_detection(args.url, args.name)

if __name__ == '__main__':
    main() 