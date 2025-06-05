#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
快速游戏爬虫 - 专门为50个游戏优化
特点：
1. 高速爬取，减少延迟
2. 更宽松的验证规则
3. 自动生成缩略图
4. 智能去重
"""

import requests
from bs4 import BeautifulSoup
import random
import time
import os
import logging
from urllib.parse import urljoin, urlparse
from datetime import datetime
import re
import threading
from queue import Queue
import subprocess
import sys

# 设置简单日志
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

# 项目配置
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GAMES_DATA_FILE = os.path.join(PROJECT_ROOT, 'src', 'data', 'games.ts')

class QuickGameCrawler:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        })
        self.found_games = []
        self.existing_titles = set()
        
        # 加载现有游戏标题
        self._load_existing_titles()
    
    def _escape_string(self, text):
        """转义字符串用于JavaScript/TypeScript输出"""
        if not text:
            return text
        
        # 转义特殊字符，反斜杠必须首先转义
        text = text.replace('\\', '\\\\')  # 反斜杠
        text = text.replace("'", "\\'")    # 单引号
        text = text.replace('"', '\\"')    # 双引号  
        text = text.replace('\n', '\\n')   # 换行符
        text = text.replace('\r', '\\r')   # 回车符
        text = text.replace('\t', '\\t')   # 制表符
        
        return text
    
    def _load_existing_titles(self):
        """加载现有游戏标题"""
        try:
            with open(GAMES_DATA_FILE, 'r', encoding='utf-8') as f:
                content = f.read()
            titles = re.findall(r'title:\s*[\'"]([^\'"]+)[\'"]', content)
            self.existing_titles = {title.lower().strip() for title in titles}
            logger.info(f"已加载 {len(self.existing_titles)} 个现有游戏标题")
        except:
            logger.warning("无法加载现有游戏，将从空开始")
    
    def crawl_itch_io_fast(self, max_games=30):
        """快速爬取itch.io游戏"""
        logger.info("🚀 快速爬取itch.io...")
        
        urls = [
            'https://itch.io/games/html5',
            'https://itch.io/games/html5/newest',
            'https://itch.io/games/html5/featured',
            'https://itch.io/games/html5/free',
        ]
        
        games = []
        
        for url in urls:
            if len(games) >= max_games:
                break
                
            try:
                response = self.session.get(url, timeout=8)
                soup = BeautifulSoup(response.text, 'html.parser')
                
                game_cells = soup.select('.game_cell')
                logger.info(f"在 {url} 找到 {len(game_cells)} 个游戏")
                
                for cell in game_cells[:15]:  # 每页最多15个
                    if len(games) >= max_games:
                        break
                    
                    try:
                        title_elem = cell.select_one('.title')
                        link_elem = cell.select_one('a')
                        
                        if not title_elem or not link_elem:
                            continue
                        
                        title = title_elem.get_text(strip=True)
                        if len(title) < 3 or title.lower() in self.existing_titles:
                            continue
                        
                        game_url = urljoin(url, link_elem['href'])
                        
                        # 简单的iframe URL推断（无需验证）
                        iframe_url = self._quick_infer_iframe(game_url)
                        
                        if iframe_url:
                            game_id = f"quick_{int(time.time())}_{len(games)}"
                            
                            game = {
                                'id': game_id,
                                'title': title,
                                'description': f"来自itch.io的HTML5游戏",
                                'category': self._quick_categorize(title),
                                'categoryId': self._quick_category_id(title),
                                'thumbnail': '/games/thumbnails/default.jpg',  # 稍后批量生成
                                'path': f'/games/{game_id}',
                                'featured': False,
                                'type': 'iframe',
                                'iframeUrl': iframe_url,
                                'addedAt': datetime.now().strftime('%Y-%m-%d'),
                                'tags': ['HTML5', '在线', 'itch.io']
                            }
                            
                            games.append(game)
                            self.existing_titles.add(title.lower())
                            logger.info(f"✅ 找到游戏: {title}")
                    
                    except Exception as e:
                        logger.debug(f"处理游戏失败: {e}")
                        continue
                
                # 短暂延迟
                time.sleep(random.uniform(0.3, 0.8))
                
            except Exception as e:
                logger.warning(f"爬取 {url} 失败: {e}")
                continue
        
        logger.info(f"🎯 itch.io爬取完成，找到 {len(games)} 个游戏")
        return games
    
    def crawl_newgrounds_fast(self, max_games=20):
        """快速爬取Newgrounds游戏"""
        logger.info("🚀 快速爬取Newgrounds...")
        
        urls = [
            'https://www.newgrounds.com/games/browse',
            'https://www.newgrounds.com/games/browse/featured',
        ]
        
        games = []
        
        for url in urls:
            if len(games) >= max_games:
                break
                
            try:
                response = self.session.get(url, timeout=8)
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Newgrounds的游戏元素
                game_items = soup.select('.item-game, .portalitem-large, .portalitem')
                logger.info(f"在 {url} 找到 {len(game_items)} 个游戏元素")
                
                for item in game_items[:10]:  # 每页最多10个
                    if len(games) >= max_games:
                        break
                    
                    try:
                        # 查找标题
                        title_elem = item.select_one('.item-title, .detail-title, h4, h3')
                        link_elem = item.select_one('a[href*="/portal/"]')
                        
                        if not title_elem or not link_elem:
                            continue
                        
                        title = title_elem.get_text(strip=True)
                        if len(title) < 3 or title.lower() in self.existing_titles:
                            continue
                        
                        game_url = urljoin(url, link_elem['href'])
                        
                        # Newgrounds的游戏页面通常可以直接嵌入
                        iframe_url = game_url
                        
                        game_id = f"ng_{int(time.time())}_{len(games)}"
                        
                        game = {
                            'id': game_id,
                            'title': title,
                            'description': f"来自Newgrounds的Flash/HTML5游戏",
                            'category': self._quick_categorize(title),
                            'categoryId': self._quick_category_id(title),
                            'thumbnail': '/games/thumbnails/default.jpg',
                            'path': f'/games/{game_id}',
                            'featured': False,
                            'type': 'iframe',
                            'iframeUrl': iframe_url,
                            'addedAt': datetime.now().strftime('%Y-%m-%d'),
                            'tags': ['HTML5', '在线', 'Newgrounds']
                        }
                        
                        games.append(game)
                        self.existing_titles.add(title.lower())
                        logger.info(f"✅ 找到游戏: {title}")
                    
                    except Exception as e:
                        logger.debug(f"处理Newgrounds游戏失败: {e}")
                        continue
                
                time.sleep(random.uniform(0.5, 1.0))
                
            except Exception as e:
                logger.warning(f"爬取 {url} 失败: {e}")
                continue
        
        logger.info(f"🎯 Newgrounds爬取完成，找到 {len(games)} 个游戏")
        return games
    
    def _quick_infer_iframe(self, game_url):
        """快速推断iframe URL"""
        parsed = urlparse(game_url)
        
        if 'itch.io' in parsed.netloc:
            # 尝试几种itch.io的常见模式
            patterns = [
                # 标准HTML5嵌入
                f"https://html-classic.itch.zone/html/{parsed.path.split('/')[-1]}/index.html",
                # 直接嵌入
                f"{game_url}/embed",
                # 原URL（某些游戏可以直接嵌入）
                game_url
            ]
            
            # 返回第一个模式（大多数情况下有效）
            return patterns[0]
        
        # 其他平台直接返回原URL
        return game_url
    
    def _quick_categorize(self, title):
        """快速分类"""
        title_lower = title.lower()
        
        if any(word in title_lower for word in ['puzzle', 'match', 'brain', 'logic']):
            return '益智'
        elif any(word in title_lower for word in ['action', 'shoot', 'fight', 'run']):
            return '动作'
        elif any(word in title_lower for word in ['card', 'poker', 'solitaire']):
            return '卡牌'
        elif any(word in title_lower for word in ['sport', 'football', 'soccer']):
            return '体育'
        elif any(word in title_lower for word in ['chess', 'strategy', 'board']):
            return '棋盘'
        else:
            return '休闲'
    
    def _quick_category_id(self, title):
        """快速获取分类ID"""
        category = self._quick_categorize(title)
        return {'休闲': '1', '益智': '2', '动作': '3', '卡牌': '4', '体育': '5', '棋盘': '6'}[category]
    
    def generate_thumbnails_for_games(self, games):
        """为游戏生成缩略图"""
        logger.info("🎨 为游戏生成缩略图...")
        
        try:
            # 先生成50个通用缩略图
            subprocess.run([
                sys.executable, 
                os.path.join(os.path.dirname(__file__), 'generate_thumbnails.py'),
                '--count', '50'
            ], check=True, capture_output=True)
            
            # 获取生成的缩略图列表
            thumbnails_dir = os.path.join(PROJECT_ROOT, 'public', 'games', 'thumbnails')
            thumbnails = [f for f in os.listdir(thumbnails_dir) 
                         if f.startswith('auto_game_') and f.endswith('.jpg')]
            thumbnails.sort()
            
            # 为每个游戏分配缩略图
            for i, game in enumerate(games):
                if i < len(thumbnails):
                    game['thumbnail'] = f'/games/thumbnails/{thumbnails[i]}'
                else:
                    # 如果缩略图不够，循环使用
                    thumb_index = i % len(thumbnails) if thumbnails else 0
                    game['thumbnail'] = f'/games/thumbnails/{thumbnails[thumb_index]}' if thumbnails else '/games/thumbnails/default.jpg'
            
            logger.info(f"✅ 缩略图生成完成，共 {len(thumbnails)} 个")
            
        except Exception as e:
            logger.warning(f"缩略图生成失败: {e}")
    
    def save_games(self, games):
        """保存游戏到文件"""
        try:
            # 读取现有数据
            with open(GAMES_DATA_FILE, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 解析现有游戏
            existing_games = self._parse_existing_games(content)
            
            # 合并游戏
            all_games = existing_games + games
            
            # 生成新文件内容
            new_content = self._generate_games_file(all_games)
            
            # 备份原文件
            backup_file = f"{GAMES_DATA_FILE}.backup.{int(time.time())}"
            import shutil
            shutil.copy2(GAMES_DATA_FILE, backup_file)
            
            # 写入新文件
            with open(GAMES_DATA_FILE, 'w', encoding='utf-8') as f:
                f.write(new_content)
            
            logger.info(f"✅ 成功保存 {len(all_games)} 个游戏")
            
        except Exception as e:
            logger.error(f"保存游戏失败: {e}")
    
    def _parse_existing_games(self, content):
        """解析现有游戏"""
        games = []
        
        try:
            # 提取games数组
            start_marker = 'export const games: Game[] = ['
            end_marker = '];'
            
            start_idx = content.find(start_marker)
            if start_idx == -1:
                return games
            
            start_idx += len(start_marker)
            end_idx = content.find(end_marker, start_idx)
            if end_idx == -1:
                return games
            
            games_str = content[start_idx:end_idx].strip()
            
            # 简单解析游戏对象
            objects = []
            depth = 0
            current_obj = ""
            
            for char in games_str:
                if char == '{':
                    if depth == 0:
                        current_obj = "{"
                    else:
                        current_obj += char
                    depth += 1
                elif char == '}':
                    depth -= 1
                    current_obj += char
                    if depth == 0:
                        objects.append(current_obj.strip())
                        current_obj = ""
                elif depth > 0:
                    current_obj += char
            
            # 解析每个游戏对象
            for obj_str in objects:
                game = {}
                patterns = {
                    'id': r"id:\s*['\"]([^'\"]+)['\"]",
                    'title': r"title:\s*['\"]([^'\"]+)['\"]",
                    'description': r"description:\s*['\"]([^'\"]*)['\"]",
                    'category': r"category:\s*['\"]([^'\"]+)['\"]",
                    'categoryId': r"categoryId:\s*['\"]([^'\"]+)['\"]",
                    'thumbnail': r"thumbnail:\s*['\"]([^'\"]+)['\"]",
                    'path': r"path:\s*['\"]([^'\"]+)['\"]",
                    'featured': r"featured:\s*(true|false)",
                    'type': r"type:\s*['\"]([^'\"]+)['\"]",
                    'iframeUrl': r"iframeUrl:\s*['\"]([^'\"]+)['\"]",
                    'addedAt': r"addedAt:\s*['\"]([^'\"]+)['\"]"
                }
                
                for field, pattern in patterns.items():
                    match = re.search(pattern, obj_str)
                    if match:
                        value = match.group(1)
                        if field == 'featured':
                            game[field] = value == 'true'
                        else:
                            game[field] = value
                
                if 'id' in game and 'title' in game:
                    games.append(game)
            
        except Exception as e:
            logger.warning(f"解析现有游戏失败: {e}")
        
        return games
    
    def _generate_games_file(self, games):
        """生成games.ts文件内容"""
        # 计算分类统计
        category_counts = {'1': 0, '2': 0, '3': 0, '4': 0, '5': 0, '6': 0}
        for game in games:
            cat_id = game.get('categoryId', '1')
            if cat_id in category_counts:
                category_counts[cat_id] += 1
        
        # 生成文件内容
        content = f"""import {{ Game, Category }} from '../types';

export const categories: Category[] = [
  {{ id: '1', name: '休闲', description: '简单有趣的休闲游戏，适合所有年龄段玩家', count: {category_counts['1']}, slug: 'casual' }},
  {{ id: '2', name: '益智', description: '锻炼大脑的益智游戏，提升思维能力', count: {category_counts['2']}, slug: 'puzzle' }},
  {{ id: '3', name: '动作', description: '刺激的动作游戏，考验你的反应速度', count: {category_counts['3']}, slug: 'action' }},
  {{ id: '4', name: '卡牌', description: '卡牌和棋牌类游戏，策略与运气的结合', count: {category_counts['4']}, slug: 'card' }},
  {{ id: '5', name: '体育', description: '各类体育模拟游戏，感受体育竞技的乐趣', count: {category_counts['5']}, slug: 'sports' }},
  {{ id: '6', name: '棋盘', description: '经典的棋盘游戏，考验战略思维', count: {category_counts['6']}, slug: 'board' }},
];

export const games: Game[] = [
"""
        
        # 生成游戏数组
        for game in games:
            tags = game.get('tags', ['休闲'])
            tags_str = ', '.join([f'"{tag}"' for tag in tags])
            
            # 转义特殊字符
            title = self._escape_string(game['title'])
            description = self._escape_string(game.get('description', ''))
            category = self._escape_string(game.get('category', '休闲'))
            thumbnail = self._escape_string(game.get('thumbnail', '/games/thumbnails/default.jpg'))
            path = self._escape_string(game.get('path', f'/games/{game['id']}'))
            iframe_url = self._escape_string(game.get('iframeUrl', ''))
            
            content += f"""  {{
    id: '{game['id']}',
    title: '{title}',
    description: '{description}',
    category: '{category}',
    categoryId: '{game.get('categoryId', '1')}',
    thumbnail: '{thumbnail}',
    path: '{path}',
    featured: {str(game.get('featured', False)).lower()},
    type: '{game.get('type', 'iframe')}',
    iframeUrl: '{iframe_url}',
    addedAt: '{game.get('addedAt', datetime.now().strftime('%Y-%m-%d'))}',
    tags: [{tags_str}]
  }},
"""
        
        content += """];

export const getFeaturedGames = (): Game[] => {
  return games.filter(game => game.featured);
};

export const getRecentGames = (limit: number = 8): Game[] => {
  return games
    .sort((a, b) => new Date(b.addedAt).getTime() - new Date(a.addedAt).getTime())
    .slice(0, limit);
};

export const getGamesByCategory = (categoryId: string): Game[] => {
  return games.filter(game => game.categoryId === categoryId);
};

export const getGameById = (id: string): Game | undefined => {
  return games.find(game => game.id === id);
};

export const getCategoryById = (id: string): Category | undefined => {
  return categories.find(category => category.id === id);
};
"""
        
        return content

def main():
    """主函数"""
    logger.info("🚀 启动快速游戏爬虫，目标50个游戏！")
    
    crawler = QuickGameCrawler()
    
    # 爬取游戏
    all_games = []
    
    # 从itch.io爬取30个游戏
    itch_games = crawler.crawl_itch_io_fast(30)
    all_games.extend(itch_games)
    
    # 从Newgrounds爬取20个游戏
    ng_games = crawler.crawl_newgrounds_fast(20)
    all_games.extend(ng_games)
    
    # 去重
    unique_games = []
    seen_titles = set()
    
    for game in all_games:
        title_key = game['title'].lower().strip()
        if title_key not in seen_titles:
            seen_titles.add(title_key)
            unique_games.append(game)
    
    logger.info(f"🎯 去重后找到 {len(unique_games)} 个唯一游戏")
    
    if unique_games:
        # 生成缩略图
        crawler.generate_thumbnails_for_games(unique_games)
        
        # 保存游戏
        crawler.save_games(unique_games)
        
        # 统计信息
        logger.info("📊 爬取统计:")
        logger.info(f"  🎮 总游戏数: {len(unique_games)}")
        
        platform_stats = {}
        for game in unique_games:
            platform = game['tags'][-1] if game['tags'] else 'Unknown'
            platform_stats[platform] = platform_stats.get(platform, 0) + 1
        
        for platform, count in platform_stats.items():
            logger.info(f"  📍 {platform}: {count} 个游戏")
        
        logger.info("🎉 快速爬虫执行完成！")
    else:
        logger.warning("❌ 没有找到任何新游戏")

if __name__ == '__main__':
    main()