#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
优化版游戏爬虫 - 高效率、多平台、智能去重
解决问题：
1. 提高爬取效率（并发爬取）
2. 增加更多游戏平台
3. 智能去重避免重复
4. 自动下载缩略图
5. 更宽松的游戏验证
"""

import requests
from bs4 import BeautifulSoup
import asyncio
import aiohttp
import json
import random
import time
import os
import logging
import re
from urllib.parse import urljoin, urlparse
from datetime import datetime
from typing import List, Dict, Optional, Set
import argparse
from PIL import Image
import io
import hashlib
import concurrent.futures
from threading import Lock

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('optimized_crawler.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# 项目配置
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GAMES_DATA_FILE = os.path.join(PROJECT_ROOT, 'src', 'data', 'games.ts')
THUMBNAILS_DIR = os.path.join(PROJECT_ROOT, 'public', 'games', 'thumbnails')

# 确保目录存在
os.makedirs(THUMBNAILS_DIR, exist_ok=True)

# 扩展的游戏平台列表
GAME_PLATFORMS = [
    {
        'name': 'itch.io',
        'urls': [
            'https://itch.io/games/html5',
            'https://itch.io/games/html5/newest',
            'https://itch.io/games/html5/featured',
            'https://itch.io/games/html5/free',
        ],
        'game_selector': '.game_cell',
        'title_selector': '.title',
        'link_selector': 'a',
        'priority': 1
    },
    {
        'name': 'Newgrounds',
        'urls': [
            'https://www.newgrounds.com/games/browse',
            'https://www.newgrounds.com/games/browse/newest',
            'https://www.newgrounds.com/games/browse/featured',
        ],
        'game_selector': '.item-game, .portalitem-large',
        'title_selector': '.item-title, .detail-title',
        'link_selector': 'a',
        'priority': 2
    },
    {
        'name': 'Kongregate',
        'urls': [
            'https://www.kongregate.com/games',
            'https://www.kongregate.com/games/new',
            'https://www.kongregate.com/games/featured',
        ],
        'game_selector': '.game-item, .gamethumb',
        'title_selector': '.game-title, h3',
        'link_selector': 'a',
        'priority': 3
    },
    {
        'name': 'CrazyGames',
        'urls': [
            'https://www.crazygames.com/c/html5',
            'https://www.crazygames.com/c/new',
            'https://www.crazygames.com/c/trending',
        ],
        'game_selector': '.game-item, .game-tile',
        'title_selector': '.game-title, h3',
        'link_selector': 'a',
        'priority': 4
    },
    {
        'name': 'Poki',
        'urls': [
            'https://poki.com/en/g/new',
            'https://poki.com/en/g/trending',
            'https://poki.com/en/g/top-rated',
        ],
        'game_selector': '.game-item, .game-card',
        'title_selector': '.game-title, h3',
        'link_selector': 'a',
        'priority': 5
    }
]

# 放宽的游戏域名白名单
GAME_DOMAINS = [
    # 原有的白名单
    'html-classic.itch.zone', 'v6p9d9t4.ssl.hwcdn.net', 'kdata.itch.zone', 'assets.itch.zone',
    'uploads.ungrounded.net', 'www.newgrounds.com', 'newgrounds.com',
    'gamejolt.net', 'cdn.gamejolt.net',
    'crazygames.com', 'embed.crazygames.com', 'poki.com', 'embed.poki.com',
    'kongregate.com', 'armor.ag', 'html5.gamedistribution.com',
    
    # 新增的游戏域名（更宽松）
    'armorgames.com', 'addictinggames.com', 'miniclip.com', 'y8.com',
    'friv.com', 'kizi.com', 'agame.com', 'silvergames.com',
    'gameforge.com', 'mousecity.com', 'games.co.uk', 'girlsgogames.com',
    'mousebreaker.com', 'gamesfreak.net', 'primarygames.com',
    'cdn.', 'static.', 'assets.', 'media.', 'content.',  # CDN域名
    'github.io', 'githubusercontent.com', 'netlify.app', 'vercel.app',  # 托管平台
]

class OptimizedGameCrawler:
    def __init__(self, max_games: int = 50):
        self.max_games = max_games
        self.found_games = []
        self.existing_titles = set()
        self.existing_urls = set()
        self.session = requests.Session()
        self.lock = Lock()
        
        # 设置请求头
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        })
        
        # 加载现有游戏避免重复
        self._load_existing_games()
    
    def _load_existing_games(self):
        """加载现有游戏以避免重复"""
        try:
            with open(GAMES_DATA_FILE, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 提取标题和URL
            title_pattern = r'title:\s*[\'"]([^\'"]+)[\'"]'
            url_pattern = r'iframeUrl:\s*[\'"]([^\'"]+)[\'"]'
            
            titles = re.findall(title_pattern, content)
            urls = re.findall(url_pattern, content)
            
            self.existing_titles = {title.lower().strip() for title in titles}
            self.existing_urls = set(urls)
            
            logger.info(f"📚 已加载 {len(self.existing_titles)} 个现有游戏标题，{len(self.existing_urls)} 个URL")
            
        except Exception as e:
            logger.warning(f"加载现有游戏失败: {e}")
    
    def is_duplicate(self, title: str, url: str = None) -> bool:
        """检查是否重复"""
        title_clean = title.lower().strip()
        
        # 检查标题重复
        if title_clean in self.existing_titles:
            return True
        
        # 检查URL重复
        if url and url in self.existing_urls:
            return True
        
        # 检查已找到的游戏中是否重复
        for game in self.found_games:
            if game['title'].lower().strip() == title_clean:
                return True
            if url and game.get('iframeUrl') == url:
                return True
        
        return False
    
    def crawl_platform(self, platform: Dict) -> List[Dict]:
        """爬取单个平台的游戏"""
        platform_games = []
        
        try:
            logger.info(f"🎮 开始爬取平台: {platform['name']}")
            
            for url in platform['urls']:
                if len(platform_games) >= 10:  # 每个平台最多10个游戏
                    break
                
                try:
                    response = self.session.get(url, timeout=10)
                    if response.status_code != 200:
                        logger.warning(f"❌ {platform['name']} - {url}: HTTP {response.status_code}")
                        continue
                    
                    soup = BeautifulSoup(response.text, 'html.parser')
                    games = self._extract_games_from_page(soup, platform, url)
                    platform_games.extend(games)
                    
                    logger.info(f"✅ {platform['name']} - {url}: 找到 {len(games)} 个游戏")
                    
                    # 短暂延迟
                    time.sleep(random.uniform(0.5, 1.0))
                    
                except Exception as e:
                    logger.warning(f"❌ {platform['name']} - {url}: {e}")
                    continue
        
        except Exception as e:
            logger.error(f"❌ 平台 {platform['name']} 爬取失败: {e}")
        
        logger.info(f"🎯 {platform['name']} 总共找到 {len(platform_games)} 个游戏")
        return platform_games
    
    def _extract_games_from_page(self, soup: BeautifulSoup, platform: Dict, base_url: str) -> List[Dict]:
        """从页面提取游戏信息"""
        games = []
        
        try:
            # 尝试配置的选择器
            game_elements = soup.select(platform['game_selector'])
            
            # 如果没找到，尝试通用选择器
            if not game_elements:
                generic_selectors = [
                    '.game', '.game-item', '.game-card', '.item', '.card',
                    '[class*="game"]', '[class*="item"]', 'article'
                ]
                for selector in generic_selectors:
                    game_elements = soup.select(selector)
                    if len(game_elements) > 3:  # 至少要有几个元素
                        break
            
            logger.debug(f"🔍 {platform['name']}: 找到 {len(game_elements)} 个游戏元素")
            
            for element in game_elements[:15]:  # 限制每页最多15个
                try:
                    game_info = self._extract_game_info(element, platform, base_url)
                    if game_info and not self.is_duplicate(game_info['title'], game_info.get('iframeUrl')):
                        games.append(game_info)
                        # 添加到已知游戏中防止重复
                        self.existing_titles.add(game_info['title'].lower().strip())
                        if game_info.get('iframeUrl'):
                            self.existing_urls.add(game_info['iframeUrl'])
                
                except Exception as e:
                    logger.debug(f"提取游戏信息失败: {e}")
                    continue
        
        except Exception as e:
            logger.warning(f"页面解析失败: {e}")
        
        return games
    
    def _extract_game_info(self, element, platform: Dict, base_url: str) -> Optional[Dict]:
        """从元素提取游戏信息"""
        try:
            # 提取标题
            title = self._extract_title(element, platform)
            if not title or len(title.strip()) < 2:
                return None
            
            # 提取链接
            link_elem = element.select_one(platform.get('link_selector', 'a'))
            if not link_elem:
                if element.name == 'a':
                    link_elem = element
                else:
                    return None
            
            game_url = urljoin(base_url, link_elem.get('href', ''))
            if not game_url:
                return None
            
            # 提取或生成iframe URL
            iframe_url = self._find_or_generate_iframe_url(game_url, platform['name'])
            if not iframe_url:
                return None
            
            # 提取缩略图
            thumbnail_url = self._extract_thumbnail_url(element, base_url)
            
            # 生成游戏信息
            game_id = f"{platform['name'].lower()}_{int(time.time())}_{random.randint(1000, 9999)}"
            
            game_info = {
                'id': game_id,
                'title': self._clean_title(title),
                'description': f"来自{platform['name']}的HTML5游戏",
                'category': self._categorize_game(title),
                'categoryId': self._get_category_id(title),
                'thumbnail': thumbnail_url or '/games/thumbnails/default.jpg',
                'path': f'/games/{game_id}',
                'featured': False,
                'type': 'iframe',
                'iframeUrl': iframe_url,
                'addedAt': datetime.now().strftime('%Y-%m-%d'),
                'tags': ['HTML5', '在线', platform['name']]
            }
            
            return game_info
            
        except Exception as e:
            logger.debug(f"提取游戏信息失败: {e}")
            return None
    
    def _extract_title(self, element, platform: Dict) -> str:
        """提取游戏标题"""
        # 尝试配置的标题选择器
        title_selectors = [platform.get('title_selector', '')]
        
        # 添加通用标题选择器
        title_selectors.extend([
            '.title', '.name', '.game-title', '.game-name',
            'h1', 'h2', 'h3', 'h4', 'h5',
            '[class*="title"]', '[class*="name"]',
            'a[title]', 'img[alt]'
        ])
        
        for selector in title_selectors:
            if not selector:
                continue
            
            try:
                elem = element.select_one(selector)
                if elem:
                    # 尝试文本内容
                    title = elem.get_text(strip=True)
                    if title and len(title) > 2:
                        return title
                    
                    # 尝试title属性
                    title = elem.get('title', '').strip()
                    if title and len(title) > 2:
                        return title
                    
                    # 尝试alt属性
                    title = elem.get('alt', '').strip()
                    if title and len(title) > 2:
                        return title
            except:
                continue
        
        # 最后尝试第一个链接的文本
        link = element.select_one('a')
        if link:
            title = link.get_text(strip=True)
            if title and len(title) > 2:
                return title
        
        return ""
    
    def _extract_thumbnail_url(self, element, base_url: str) -> Optional[str]:
        """提取缩略图URL"""
        img_selectors = ['img', '.thumb img', '.thumbnail img', '.game-thumb img']
        
        for selector in img_selectors:
            try:
                img = element.select_one(selector)
                if img:
                    src = img.get('src') or img.get('data-src') or img.get('data-lazy')
                    if src:
                        full_url = urljoin(base_url, src)
                        if self._is_valid_image_url(full_url):
                            return self._download_and_save_thumbnail(full_url)
            except:
                continue
        
        return None
    
    def _is_valid_image_url(self, url: str) -> bool:
        """检查是否是有效的图片URL"""
        if not url:
            return False
        
        # 检查文件扩展名
        parsed = urlparse(url.lower())
        path = parsed.path
        
        image_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.webp']
        if any(path.endswith(ext) for ext in image_extensions):
            return True
        
        # 检查是否包含图片相关参数
        if any(keyword in url.lower() for keyword in ['thumb', 'preview', 'cover', 'image']):
            return True
        
        return False
    
    def _download_and_save_thumbnail(self, url: str) -> str:
        """下载并保存缩略图"""
        try:
            response = self.session.get(url, timeout=5, stream=True)
            if response.status_code != 200:
                return None
            
            # 检查内容类型
            content_type = response.headers.get('content-type', '').lower()
            if not any(img_type in content_type for img_type in ['image/jpeg', 'image/png', 'image/gif', 'image/webp']):
                return None
            
            # 生成文件名
            url_hash = hashlib.md5(url.encode()).hexdigest()[:8]
            timestamp = int(time.time())
            filename = f"game_{timestamp}_{url_hash}.jpg"
            filepath = os.path.join(THUMBNAILS_DIR, filename)
            
            # 下载并处理图片
            img_data = response.content
            
            # 尝试用PIL处理图片（转换格式、调整大小）
            try:
                img = Image.open(io.BytesIO(img_data))
                
                # 转换为RGB（去除透明通道）
                if img.mode in ('RGBA', 'LA', 'P'):
                    img = img.convert('RGB')
                
                # 调整大小（最大300x200）
                img.thumbnail((300, 200), Image.Resampling.LANCZOS)
                
                # 保存
                img.save(filepath, 'JPEG', quality=85, optimize=True)
                
                logger.debug(f"✅ 下载缩略图: {filename}")
                return f'/games/thumbnails/{filename}'
                
            except Exception as e:
                # 如果PIL处理失败，直接保存原文件
                with open(filepath, 'wb') as f:
                    f.write(img_data)
                
                logger.debug(f"✅ 下载缩略图（原格式）: {filename}")
                return f'/games/thumbnails/{filename}'
        
        except Exception as e:
            logger.debug(f"下载缩略图失败 {url}: {e}")
            return None
    
    def _find_or_generate_iframe_url(self, game_url: str, platform_name: str) -> Optional[str]:
        """查找或生成iframe URL"""
        try:
            # 对于某些平台，可以直接推断iframe URL
            if platform_name.lower() == 'itch.io':
                return self._generate_itch_iframe_url(game_url)
            elif platform_name.lower() == 'newgrounds':
                return self._generate_newgrounds_iframe_url(game_url)
            elif platform_name.lower() == 'kongregate':
                return self._generate_kongregate_iframe_url(game_url)
            elif platform_name.lower() == 'crazygames':
                return self._generate_crazygames_iframe_url(game_url)
            
            # 尝试访问游戏页面查找iframe
            response = self.session.get(game_url, timeout=5)
            if response.status_code != 200:
                return None
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # 查找iframe
            iframes = soup.select('iframe[src]')
            for iframe in iframes:
                src = iframe.get('src')
                if src and self._is_valid_game_iframe(src):
                    return urljoin(game_url, src)
            
            # 查找其他嵌入方式
            embeds = soup.select('[data-src], [data-game-url], [data-embed-url]')
            for embed in embeds:
                for attr in ['data-src', 'data-game-url', 'data-embed-url']:
                    url = embed.get(attr)
                    if url and self._is_valid_game_iframe(url):
                        return urljoin(game_url, url)
            
            return None
            
        except Exception as e:
            logger.debug(f"查找iframe失败 {game_url}: {e}")
            return None
    
    def _generate_itch_iframe_url(self, game_url: str) -> Optional[str]:
        """为itch.io生成iframe URL"""
        try:
            # itch.io的游戏通常有标准的iframe格式
            parsed = urlparse(game_url)
            if 'itch.io' in parsed.netloc:
                # 尝试几种常见的iframe模式
                patterns = [
                    f"https://html-classic.itch.zone/html/{parsed.path.split('/')[-1]}/index.html",
                    f"{game_url}/embed",
                    f"{game_url.rstrip('/')}/embed"
                ]
                
                for pattern in patterns:
                    if self._test_iframe_url(pattern):
                        return pattern
            
            return game_url  # 作为备选
        except:
            return None
    
    def _generate_newgrounds_iframe_url(self, game_url: str) -> Optional[str]:
        """为Newgrounds生成iframe URL"""
        # Newgrounds的游戏页面通常就是可嵌入的
        return game_url
    
    def _generate_kongregate_iframe_url(self, game_url: str) -> Optional[str]:
        """为Kongregate生成iframe URL"""
        try:
            parsed = urlparse(game_url)
            if '/games/' in parsed.path:
                # Kongregate的iframe模式
                game_id = parsed.path.split('/')[-1]
                return f"https://www.kongregate.com/games/{game_id}/embed"
        except:
            pass
        return game_url
    
    def _generate_crazygames_iframe_url(self, game_url: str) -> Optional[str]:
        """为CrazyGames生成iframe URL"""
        try:
            parsed = urlparse(game_url)
            if '/game/' in parsed.path:
                return f"https://embed.crazygames.com{parsed.path}"
        except:
            pass
        return game_url
    
    def _test_iframe_url(self, url: str) -> bool:
        """测试iframe URL是否有效"""
        try:
            response = self.session.head(url, timeout=3)
            return response.status_code == 200
        except:
            return False
    
    def _is_valid_game_iframe(self, url: str) -> bool:
        """检查是否是有效的游戏iframe URL（更宽松的验证）"""
        if not url:
            return False
        
        url_lower = url.lower()
        parsed = urlparse(url)
        
        # 白名单域名检查（更宽松）
        for domain in GAME_DOMAINS:
            if domain in parsed.netloc or domain in url_lower:
                return True
        
        # 游戏相关路径检查
        game_patterns = [
            '/game/', '/games/', '/play/', '/embed/', '/player/',
            '/html5/', '/swf/', '/unity/', '/webgl/', '/canvas/',
            'game.html', 'index.html', 'play.html'
        ]
        
        for pattern in game_patterns:
            if pattern in url_lower:
                return True
        
        # 避免明显的非游戏内容
        exclude_patterns = [
            'ads', 'analytics', 'tracking', 'social', 'comment',
            'youtube', 'facebook', 'twitter', 'discord'
        ]
        
        for pattern in exclude_patterns:
            if pattern in url_lower:
                return False
        
        # 默认接受（更宽松的策略）
        return True
    
    def _clean_title(self, title: str) -> str:
        """清理游戏标题"""
        # 移除常见的后缀和前缀
        patterns_to_remove = [
            r'\s*-\s*Play Online.*$',
            r'\s*\|\s*Free Game.*$',
            r'\s*-\s*Browser Game.*$',
            r'\s*Online.*$',
            r'^\s*Play\s+',
            r'\s*Game\s*$'
        ]
        
        for pattern in patterns_to_remove:
            title = re.sub(pattern, '', title, flags=re.IGNORECASE)
        
        return title.strip()
    
    def _categorize_game(self, title: str) -> str:
        """自动分类游戏"""
        title_lower = title.lower()
        
        if any(word in title_lower for word in ['puzzle', 'match', 'brain', 'logic', 'sudoku', 'tetris']):
            return '益智'
        elif any(word in title_lower for word in ['action', 'shoot', 'fight', 'run', 'jump', 'platform']):
            return '动作'
        elif any(word in title_lower for word in ['card', 'poker', 'solitaire', 'blackjack']):
            return '卡牌'
        elif any(word in title_lower for word in ['sport', 'football', 'soccer', 'basketball', 'tennis']):
            return '体育'
        elif any(word in title_lower for word in ['chess', 'checkers', 'board', 'strategy']):
            return '棋盘'
        else:
            return '休闲'
    
    def _get_category_id(self, title: str) -> str:
        """获取分类ID"""
        category = self._categorize_game(title)
        category_map = {
            '休闲': '1',
            '益智': '2',
            '动作': '3',
            '卡牌': '4',
            '体育': '5',
            '棋盘': '6'
        }
        return category_map.get(category, '1')
    
    def crawl_all_platforms(self) -> List[Dict]:
        """并发爬取所有平台"""
        logger.info(f"🚀 开始并发爬取 {len(GAME_PLATFORMS)} 个平台，目标 {self.max_games} 个游戏")
        
        all_games = []
        
        # 使用线程池并发爬取
        with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
            future_to_platform = {
                executor.submit(self.crawl_platform, platform): platform 
                for platform in GAME_PLATFORMS
            }
            
            for future in concurrent.futures.as_completed(future_to_platform):
                platform = future_to_platform[future]
                try:
                    games = future.result(timeout=60)  # 每个平台最多60秒
                    all_games.extend(games)
                    
                    logger.info(f"✅ {platform['name']} 完成，找到 {len(games)} 个游戏")
                    
                    # 如果已经找到足够的游戏，可以提前停止
                    if len(all_games) >= self.max_games:
                        logger.info(f"🎯 已达到目标数量 {self.max_games}，停止爬取")
                        break
                        
                except Exception as e:
                    logger.error(f"❌ {platform['name']} 爬取失败: {e}")
        
        # 去重和排序
        unique_games = self._deduplicate_games(all_games)
        
        # 限制数量
        final_games = unique_games[:self.max_games]
        
        logger.info(f"🎉 爬取完成！总共找到 {len(final_games)} 个唯一游戏")
        return final_games
    
    def _deduplicate_games(self, games: List[Dict]) -> List[Dict]:
        """去重游戏"""
        seen_titles = set()
        seen_urls = set()
        unique_games = []
        
        for game in games:
            title_key = game['title'].lower().strip()
            url_key = game.get('iframeUrl', '')
            
            if title_key not in seen_titles and url_key not in seen_urls:
                seen_titles.add(title_key)
                if url_key:
                    seen_urls.add(url_key)
                unique_games.append(game)
        
        logger.info(f"🔄 去重完成: {len(unique_games)}/{len(games)} 个唯一游戏")
        return unique_games
    
    def save_games(self, games: List[Dict]):
        """保存游戏到文件"""
        try:
            # 读取现有数据
            existing_games = []
            try:
                with open(GAMES_DATA_FILE, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # 解析现有游戏
                existing_games = self._parse_existing_games(content)
                
            except Exception as e:
                logger.warning(f"读取现有游戏失败: {e}")
            
            # 合并游戏
            all_games = existing_games + games
            
            # 去重
            all_games = self._deduplicate_games(all_games)
            
            # 生成新文件内容
            new_content = self._generate_games_file_content(all_games)
            
            # 备份原文件
            backup_file = f"{GAMES_DATA_FILE}.backup.{int(time.time())}"
            if os.path.exists(GAMES_DATA_FILE):
                import shutil
                shutil.copy2(GAMES_DATA_FILE, backup_file)
                logger.info(f"📁 已备份原文件: {backup_file}")
            
            # 写入新文件
            with open(GAMES_DATA_FILE, 'w', encoding='utf-8') as f:
                f.write(new_content)
            
            logger.info(f"✅ 成功保存 {len(all_games)} 个游戏到 {GAMES_DATA_FILE}")
            
        except Exception as e:
            logger.error(f"保存游戏失败: {e}")
    
    def _parse_existing_games(self, content: str) -> List[Dict]:
        """解析现有游戏数据"""
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
            
            # 简单的游戏对象解析
            game_objects = self._extract_game_objects(games_str)
            
            for game_obj in game_objects:
                game_data = self._parse_game_object(game_obj)
                if game_data:
                    games.append(game_data)
            
            logger.info(f"📚 解析到 {len(games)} 个现有游戏")
            
        except Exception as e:
            logger.warning(f"解析现有游戏失败: {e}")
        
        return games
    
    def _extract_game_objects(self, games_str: str) -> List[str]:
        """提取游戏对象字符串"""
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
        
        return objects
    
    def _parse_game_object(self, obj_str: str) -> Optional[Dict]:
        """解析单个游戏对象"""
        try:
            game = {}
            
            # 提取各个字段
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
            
            return game if 'id' in game and 'title' in game else None
            
        except Exception as e:
            logger.debug(f"解析游戏对象失败: {e}")
            return None
    
    def _generate_games_file_content(self, games: List[Dict]) -> str:
        """生成games.ts文件内容"""
        # 计算分类统计
        category_counts = {'1': 0, '2': 0, '3': 0, '4': 0, '5': 0, '6': 0}
        for game in games:
            cat_id = game.get('categoryId', '1')
            if cat_id in category_counts:
                category_counts[cat_id] += 1
        
        # 生成文件内容
        content = """import { Game, Category } from '../types';

export const categories: Category[] = [
  { id: '1', name: '休闲', description: '简单有趣的休闲游戏，适合所有年龄段玩家', count: """ + str(category_counts['1']) + """, slug: 'casual' },
  { id: '2', name: '益智', description: '锻炼大脑的益智游戏，提升思维能力', count: """ + str(category_counts['2']) + """, slug: 'puzzle' },
  { id: '3', name: '动作', description: '刺激的动作游戏，考验你的反应速度', count: """ + str(category_counts['3']) + """, slug: 'action' },
  { id: '4', name: '卡牌', description: '卡牌和棋牌类游戏，策略与运气的结合', count: """ + str(category_counts['4']) + """, slug: 'card' },
  { id: '5', name: '体育', description: '各类体育模拟游戏，感受体育竞技的乐趣', count: """ + str(category_counts['5']) + """, slug: 'sports' },
  { id: '6', name: '棋盘', description: '经典的棋盘游戏，考验战略思维', count: """ + str(category_counts['6']) + """, slug: 'board' },
];

export const games: Game[] = [
"""
        
        # 生成游戏数组
        for game in games:
            content += "  {\n"
            content += f"    id: '{game['id']}',\n"
            content += f"    title: '{game['title']}',\n"
            content += f"    description: '{game.get('description', '')}',\n"
            content += f"    category: '{game.get('category', '休闲')}',\n"
            content += f"    categoryId: '{game.get('categoryId', '1')}',\n"
            content += f"    thumbnail: '{game.get('thumbnail', '/games/thumbnails/default.jpg')}',\n"
            content += f"    path: '{game.get('path', f'/games/{game['id']}')}',\n"
            content += f"    featured: {str(game.get('featured', False)).lower()},\n"
            content += f"    type: '{game.get('type', 'iframe')}',\n"
            content += f"    iframeUrl: '{game.get('iframeUrl', '')}',\n"
            content += f"    addedAt: '{game.get('addedAt', datetime.now().strftime('%Y-%m-%d'))}',\n"
            
            tags = game.get('tags', ['休闲'])
            tags_str = ', '.join([f'"{tag}"' for tag in tags])
            content += f"    tags: [{tags_str}]\n"
            content += "  },\n"
        
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
    parser = argparse.ArgumentParser(description='优化版游戏爬虫 - 高效率、多平台、智能去重')
    parser.add_argument('--max-games', type=int, default=50, help='最大爬取游戏数量')
    parser.add_argument('--platforms', nargs='+', 
                       choices=['itch.io', 'newgrounds', 'kongregate', 'crazygames', 'poki'],
                       help='指定要爬取的平台')
    
    args = parser.parse_args()
    
    # 过滤平台
    if args.platforms:
        global GAME_PLATFORMS
        GAME_PLATFORMS = [p for p in GAME_PLATFORMS if p['name'].lower() in [name.lower() for name in args.platforms]]
        logger.info(f"🎯 仅爬取指定平台: {[p['name'] for p in GAME_PLATFORMS]}")
    
    # 创建爬虫实例
    crawler = OptimizedGameCrawler(max_games=args.max_games)
    
    # 开始爬取
    games = crawler.crawl_all_platforms()
    
    if games:
        # 保存游戏
        crawler.save_games(games)
        
        # 输出统计信息
        logger.info("📊 爬取统计:")
        logger.info(f"  📈 总游戏数: {len(games)}")
        
        platform_stats = {}
        for game in games:
            platform = game['tags'][-1] if game['tags'] else 'Unknown'
            platform_stats[platform] = platform_stats.get(platform, 0) + 1
        
        for platform, count in platform_stats.items():
            logger.info(f"  🎮 {platform}: {count} 个游戏")
        
        # 统计缩略图
        thumbnails_with_custom = sum(1 for game in games if not game['thumbnail'].endswith('default.jpg'))
        logger.info(f"  🖼️ 自定义缩略图: {thumbnails_with_custom}/{len(games)} 个")
        
        logger.info("🎉 优化版爬虫执行完成！")
    else:
        logger.warning("❌ 没有找到任何游戏")

if __name__ == '__main__':
    main()