#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
增强版游戏爬虫 - 专门收集可本地运行或iframe嵌入的游戏
确保所有游戏都不需要跳转外链，可以直接在平台内游玩
"""

import requests
from bs4 import BeautifulSoup
import json
import random
import time
import os
import re
import logging
from datetime import datetime
from urllib.parse import urljoin, urlparse
from typing import List, Dict, Optional

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('enhanced_crawler.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# 项目配置
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GAMES_DATA_FILE = os.path.join(PROJECT_ROOT, 'src', 'data', 'games.ts')

# 专门的HTML5游戏平台
HTML5_GAME_SITES = [
    {
        'name': 'itch.io HTML5',
        'url': 'https://itch.io/games/html5',
        'iframe_selector': 'iframe[src*="html-classic.itch.zone"]',
        'game_selector': '.game_cell',
        'title_selector': '.title',
        'desc_selector': '.game_text'
    },
    {
        'name': 'GameJolt HTML5',
        'url': 'https://gamejolt.com/games/best/html',
        'iframe_selector': 'iframe[src*="gamejolt"]',
        'game_selector': '.game-listing-item',
        'title_selector': '.game-title',
        'desc_selector': '.game-description'
    },
    {
        'name': 'CrazyGames',
        'url': 'https://www.crazygames.com/c/html5',
        'iframe_selector': 'iframe[src*="crazygames"]',
        'game_selector': '.game-item',
        'title_selector': '.game-title',
        'desc_selector': '.game-description'
    }
]

# 游戏分类映射
CATEGORY_MAPPING = {
    'puzzle': '益智', 'action': '动作', 'adventure': '冒险',
    'arcade': '休闲', 'casual': '休闲', 'strategy': '策略',
    'sports': '体育', 'racing': '竞速', 'shooter': '射击',
    'platformer': '平台', 'rpg': '角色扮演', 'simulation': '模拟',
    'card': '卡牌', 'board': '棋盘', 'music': '音乐'
}

CATEGORY_ID_MAPPING = {
    '休闲': '1', '益智': '2', '动作': '3',
    '卡牌': '4', '体育': '5', '棋盘': '6'
}

class EnhancedGameCrawler:
    """增强版游戏爬虫，专注于可嵌入游戏"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        self.found_games = []
    
    def is_embeddable_url(self, url: str) -> bool:
        """检查URL是否可以嵌入"""
        try:
            # 检查是否是已知的可嵌入域名
            embeddable_domains = [
                'html-classic.itch.zone',  # itch.io嵌入式游戏
                'gamejolt.com/embed',      # GameJolt嵌入
                'crazygames.com/embed',    # CrazyGames嵌入
                'poki.com/embed',          # Poki嵌入
                'kongregate.com/embed',    # Kongregate嵌入
                'newgrounds.com/embed'     # Newgrounds嵌入
            ]
            
            for domain in embeddable_domains:
                if domain in url:
                    return True
            
            # 检查是否包含HTML5游戏文件
            if any(ext in url.lower() for ext in ['.html', '.htm', '/play', '/game']):
                # 发送HEAD请求检查X-Frame-Options
                try:
                    response = self.session.head(url, timeout=5)
                    frame_options = response.headers.get('X-Frame-Options', '').upper()
                    return frame_options not in ['DENY', 'SAMEORIGIN']
                except:
                    return False
            
            return False
            
        except Exception as e:
            logger.error(f"检查URL可嵌入性失败: {url}, {e}")
            return False
    
    def extract_iframe_games(self, site_config: Dict) -> List[Dict]:
        """从指定网站提取iframe游戏"""
        games = []
        
        try:
            logger.info(f"正在爬取: {site_config['name']}")
            response = self.session.get(site_config['url'], timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            game_elements = soup.select(site_config['game_selector'])
            
            for element in game_elements[:10]:  # 限制每个网站10个游戏
                try:
                    # 提取游戏信息
                    title_elem = element.select_one(site_config['title_selector'])
                    if not title_elem:
                        continue
                    
                    title = title_elem.get_text(strip=True)
                    if not title or len(title) < 3:
                        continue
                    
                    # 获取游戏链接
                    link_elem = element.select_one('a[href]')
                    if not link_elem:
                        continue
                    
                    game_url = urljoin(site_config['url'], link_elem['href'])
                    
                    # 获取游戏页面，查找iframe
                    game_response = self.session.get(game_url, timeout=10)
                    game_soup = BeautifulSoup(game_response.text, 'html.parser')
                    
                    # 查找可嵌入的iframe
                    iframe = game_soup.select_one(site_config['iframe_selector'])
                    if iframe and iframe.get('src'):
                        iframe_url = urljoin(game_url, iframe['src'])
                        
                        if self.is_embeddable_url(iframe_url):
                            # 提取描述
                            desc_elem = element.select_one(site_config.get('desc_selector', '.description'))
                            description = desc_elem.get_text(strip=True) if desc_elem else f"一款有趣的HTML5游戏"
                            
                            # 提取缩略图
                            img_elem = element.select_one('img[src]')
                            thumbnail_url = urljoin(site_config['url'], img_elem['src']) if img_elem else None
                            
                            game_info = {
                                'title': title,
                                'description': description,
                                'category': '休闲',  # 默认分类
                                'thumbnail_url': thumbnail_url,
                                'type': 'iframe',
                                'iframe_url': iframe_url,
                                'source': site_config['name']
                            }
                            
                            # 验证游戏数据
                            if self.validate_game_data(game_info):
                                games.append(game_info)
                                logger.info(f"✅ 找到可嵌入游戏: {title}")
                            else:
                                logger.info(f"❌ 游戏数据验证失败，跳过: {title}")
                    
                    time.sleep(random.uniform(1, 2))  # 避免请求过快
                    
                except Exception as e:
                    logger.error(f"提取游戏失败: {e}")
                    continue
            
        except Exception as e:
            logger.error(f"爬取网站失败 {site_config['name']}: {e}")
        
        return games
    
    def generate_game_data(self, games: List[Dict]) -> List[Dict]:
        """生成最终的游戏数据"""
        processed_games = []
        
        for i, game in enumerate(games):
            try:
                game_id = str(100 + i)  # 从100开始编号，避免与现有游戏冲突
                
                game_data = {
                    'id': game_id,
                    'title': game['title'][:50],  # 限制标题长度
                    'description': game['description'][:200],  # 限制描述长度
                    'category': game['category'],
                    'categoryId': CATEGORY_ID_MAPPING.get(game['category'], '1'),
                    'thumbnail': '/games/thumbnails/default.jpg',  # 使用默认缩略图
                    'path': f'/games/{game_id}',
                    'featured': False,
                    'type': 'iframe',
                    'iframeUrl': game['iframe_url'],
                    'addedAt': datetime.now().strftime('%Y-%m-%d'),
                    'tags': [game['category'], 'HTML5', '在线']
                }
                
                processed_games.append(game_data)
                logger.info(f"✅ 生成游戏数据: {game_data['title']}")
                
            except Exception as e:
                logger.error(f"生成游戏数据失败: {e}")
                continue
        
        return processed_games
    
    def save_to_json(self, games: List[Dict], filename: str = 'enhanced_games.json'):
        """保存游戏数据到JSON文件"""
        try:
            filepath = os.path.join(PROJECT_ROOT, 'scripts', filename)
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(games, f, ensure_ascii=False, indent=2)
            logger.info(f"✅ 保存游戏数据到: {filepath}")
        except Exception as e:
            logger.error(f"保存JSON文件失败: {e}")
    
    def run(self):
        """运行增强版爬虫"""
        logger.info("🚀 开始运行增强版游戏爬虫...")
        
        all_games = []
        
        # 爬取各个HTML5游戏网站
        for site_config in HTML5_GAME_SITES:
            try:
                games = self.extract_iframe_games(site_config)
                all_games.extend(games)
                time.sleep(random.uniform(3, 5))  # 网站间延迟
            except Exception as e:
                logger.error(f"爬取网站失败: {e}")
                continue
        
        logger.info(f"🎮 总共找到 {len(all_games)} 个可嵌入游戏")
        
        if all_games:
            # 生成游戏数据
            processed_games = self.generate_game_data(all_games)
            
            # 保存到JSON文件
            self.save_to_json(processed_games)
            
            logger.info(f"✅ 增强版爬虫完成！成功处理 {len(processed_games)} 个游戏")
        else:
            logger.warning("❌ 没有找到可嵌入的游戏")

    def validate_game_data(self, game_info: Dict) -> bool:
        """验证游戏数据是否有效"""
        try:
            title = game_info.get('title', '').strip()
            description = game_info.get('description', '').strip()
            iframe_url = game_info.get('iframe_url', '')
            
            # 1. 检查标题有效性
            invalid_titles = [
                'unleash the gamer',
                'play games',
                'free games',
                'online games',
                'game portal',
                'gaming platform',
                'entertainment',
                'company',
                'developer',
                'publisher',
                'studio'
            ]
            
            title_lower = title.lower()
            if any(invalid in title_lower for invalid in invalid_titles):
                logger.info(f"❌ 跳过无效标题: {title}")
                return False
            
            # 2. 检查标题长度和格式
            if len(title) < 3 or len(title) > 100:
                logger.info(f"❌ 标题长度不合适: {title}")
                return False
            
            # 3. 检查是否是公司/网站介绍
            company_keywords = [
                'we develop',
                'we publish',
                'we reach',
                'million players',
                'international',
                'company',
                'entertainment company',
                'game developer',
                'our audience'
            ]
            
            desc_lower = description.lower()
            if any(keyword in desc_lower for keyword in company_keywords):
                logger.info(f"❌ 跳过公司介绍: {title}")
                return False
            
            # 4. 检查iframe URL有效性
            if not iframe_url or not self.is_valid_game_url(iframe_url):
                logger.info(f"❌ 无效的游戏URL: {iframe_url}")
                return False
            
            # 5. 检查是否是网站首页或分类页
            invalid_url_patterns = [
                '/games$',
                '/games/$',
                'miniclip.com/games$',
                'itch.io/games',
                'gamejolt.com/games',
                'newgrounds.com/games',
                '/browse$',
                '/category',
                '/tag/',
                'youtube.com/embed'
            ]
            
            for pattern in invalid_url_patterns:
                if re.search(pattern, iframe_url, re.IGNORECASE):
                    logger.info(f"❌ 跳过网站首页/分类页: {iframe_url}")
                    return False
            
            logger.info(f"✅ 游戏数据验证通过: {title}")
            return True
            
        except Exception as e:
            logger.error(f"验证游戏数据失败: {e}")
            return False
    
    def is_valid_game_url(self, url: str) -> bool:
        """检查是否是有效的游戏URL"""
        try:
            parsed = urlparse(url)
            
            # 检查URL格式
            if not parsed.scheme or not parsed.netloc:
                return False
            
            # 检查是否是已知的游戏文件
            valid_game_indicators = [
                'html-classic.itch.zone',
                '/play/',
                '/game/',
                'index.html',
                '.html',
                '/embed/',
                'gamejolt.com/games/',
                'newgrounds.com/portal/view/'
            ]
            
            return any(indicator in url.lower() for indicator in valid_game_indicators)
            
        except Exception:
            return False

def main():
    """主函数"""
    crawler = EnhancedGameCrawler()
    crawler.run()

if __name__ == '__main__':
    main() 