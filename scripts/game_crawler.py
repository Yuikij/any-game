#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
游戏爬虫脚本 - 全网搜索游戏资源并扩充项目游戏库
支持搜索iframe嵌入式游戏和HTML静态游戏两种类型
"""

import requests
from bs4 import BeautifulSoup
import json
import random
import time
import os
import re
import hashlib
from urllib.parse import urljoin, urlparse, quote
from http.client import RemoteDisconnected
from requests.exceptions import RequestException, Timeout
from tenacity import retry, stop_after_attempt, wait_fixed
import logging
from datetime import datetime
from typing import List, Dict, Optional, Tuple

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('game_crawler.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# 项目配置
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GAMES_DATA_FILE = os.path.join(PROJECT_ROOT, 'src', 'data', 'games.ts')
THUMBNAILS_DIR = os.path.join(PROJECT_ROOT, 'public', 'games', 'thumbnails')
STATIC_GAMES_DIR = os.path.join(PROJECT_ROOT, 'public', 'games')

# 搜索配置 - 专注于HTML5和可嵌入游戏
SEARCH_QUERIES = [
    'site:itch.io HTML5 games embed',
    'site:gamejolt.com HTML5 browser games',
    'site:newgrounds.com HTML5 games',
    'site:kongregate.com HTML5 games',
    'site:armorgames.com HTML5 games',
    'site:crazygames.com HTML5 games',
    'site:poki.com HTML5 games',
    'HTML5 games iframe embed',
    'browser games no download',
    'online games HTML5 canvas',
    'HTML5游戏 在线玩',
    '网页游戏 HTML5',
    '免费HTML5游戏'
]

# 已知游戏平台种子URL - 专注于可嵌入游戏的平台
SEED_URLS = [
    'https://itch.io/games/html5',              # itch.io HTML5游戏
    'https://html-classic.itch.zone/',         # itch.io嵌入式游戏
    'https://gamejolt.com/games/best/html',    # GameJolt HTML5游戏
    'https://www.newgrounds.com/games/browse/tag/html5', # Newgrounds HTML5
    'https://www.kongregate.com/games/new?tag=HTML5',    # Kongregate HTML5
    'https://armorgames.com/search?type=games&q=html5',  # ArmorGames HTML5
    'https://poki.com/en/g/html5',             # Poki HTML5游戏
    'https://www.crazygames.com/c/html5',      # CrazyGames HTML5
    'https://html5games.com/',                 # 专门的HTML5游戏网站
    'https://www.gameflare.com/online-games/', # GameFlare在线游戏
    'https://www.silvergames.com/html5',       # SilverGames HTML5
    'https://www.agame.com/games/html5'        # Agame HTML5游戏
]

# 模拟浏览器请求头
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
    'Accept-Encoding': 'gzip, deflate, br',
    'Connection': 'keep-alive',
    'Upgrade-Insecure-Requests': '1'
}

# 游戏分类映射
CATEGORY_MAPPING = {
    'puzzle': '益智',
    'action': '动作', 
    'adventure': '冒险',
    'arcade': '休闲',
    'casual': '休闲',
    'strategy': '策略',
    'sports': '体育',
    'racing': '竞速',
    'shooter': '射击',
    'platformer': '平台',
    'rpg': '角色扮演',
    'simulation': '模拟',
    'card': '卡牌',
    'board': '棋盘',
    'music': '音乐',
    'educational': '教育',
    'multiplayer': '多人',
    'idle': '放置',
    'clicker': '点击',
    'tower-defense': '塔防'
}

# 默认分类ID映射
CATEGORY_ID_MAPPING = {
    '休闲': '1',
    '益智': '2', 
    '动作': '3',
    '卡牌': '4',
    '体育': '5',
    '棋盘': '6'
}

class GameCrawler:
    """游戏爬虫类"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update(HEADERS)
        self.found_games = []
        self.processed_urls = set()
        
        # 确保目录存在
        os.makedirs(THUMBNAILS_DIR, exist_ok=True)
        os.makedirs(STATIC_GAMES_DIR, exist_ok=True)
    
    @retry(stop=stop_after_attempt(3), wait=wait_fixed(2))
    def fetch_page(self, url: str, timeout: int = 10) -> Optional[BeautifulSoup]:
        """获取网页内容并解析"""
        try:
            logger.info(f"正在获取页面: {url}")
            response = self.session.get(url, timeout=timeout)
            response.raise_for_status()
            
            # 检测编码
            if response.encoding == 'ISO-8859-1':
                response.encoding = response.apparent_encoding
            
            soup = BeautifulSoup(response.text, 'html.parser')
            return soup
            
        except (RequestException, Timeout) as e:
            logger.error(f"获取页面失败 {url}: {e}")
            raise
        except Exception as e:
            logger.error(f"解析页面失败 {url}: {e}")
            return None
    
    def extract_game_info(self, soup: BeautifulSoup, base_url: str) -> List[Dict]:
        """从页面中提取游戏信息"""
        games = []
        
        # 不同网站的游戏选择器
        game_selectors = [
            # itch.io
            '.game_cell, .game_grid_widget',
            # GameJolt
            '.game-thumbnail, .game-listing-item',
            # Newgrounds
            '.item-portalitem, .portal-item',
            # Kongregate
            '.game-item, .game-thumb',
            # ArmorGames
            '.game-item, .thumb',
            # 通用选择器
            '[class*="game"], [class*="item"], article, .card'
        ]
        
        for selector in game_selectors:
            game_elements = soup.select(selector)
            if game_elements:
                logger.info(f"使用选择器 '{selector}' 找到 {len(game_elements)} 个游戏元素")
                break
        
        for element in game_elements[:20]:  # 限制每页最多处理20个游戏
            try:
                game_info = self._extract_single_game(element, base_url)
                if game_info:
                    games.append(game_info)
            except Exception as e:
                logger.error(f"提取游戏信息失败: {e}")
                continue
        
        return games
    
    def _extract_single_game(self, element: BeautifulSoup, base_url: str) -> Optional[Dict]:
        """提取单个游戏的信息"""
        try:
            # 提取标题
            title_selectors = ['h3', 'h4', '.title', '.name', '.game-title', 'a[title]', 'img[alt]']
            title = None
            for selector in title_selectors:
                title_elem = element.select_one(selector)
                if title_elem:
                    title = title_elem.get('title') or title_elem.get('alt') or title_elem.get_text(strip=True)
                    if title and len(title) > 2:
                        break
            
            if not title:
                return None
            
            # 提取链接
            link_elem = element.select_one('a[href]')
            if not link_elem:
                return None
            
            game_url = urljoin(base_url, link_elem['href'])
            
            # 检查是否已处理过
            if game_url in self.processed_urls:
                return None
            self.processed_urls.add(game_url)
            
            # 判断游戏类型 - 这里是关键过滤步骤
            game_type, game_data = self._determine_game_type(game_url)
            
            # 如果无法确定游戏类型或不适合嵌入，跳过这个游戏
            if not game_type or not game_data:
                logger.info(f"跳过不适合嵌入的游戏: {title}")
                return None
            
            # 提取缩略图
            thumbnail_selectors = ['img[src]', '.thumbnail img', '.icon img']
            thumbnail_url = None
            for selector in thumbnail_selectors:
                img_elem = element.select_one(selector)
                if img_elem and img_elem.get('src'):
                    thumbnail_url = urljoin(base_url, img_elem['src'])
                    break
            
            # 提取描述
            desc_selectors = ['.description', '.summary', '.excerpt', 'p']
            description = None
            for selector in desc_selectors:
                desc_elem = element.select_one(selector)
                if desc_elem:
                    description = desc_elem.get_text(strip=True)
                    if description and len(description) > 10:
                        break
            
            # 提取分类
            category = self._extract_category(element, base_url)
            
            game_info = {
                'title': self._clean_title(title),
                'description': description or f"一款有趣的{category}游戏",
                'category': category,
                'thumbnail_url': thumbnail_url,
                'game_url': game_url,
                'type': game_type,
                'game_data': game_data
            }
            
            # 验证游戏数据
            if not self.validate_game_data(game_info):
                logger.info(f"❌ 游戏数据验证失败，跳过: {title}")
                return None
            
            logger.info(f"✅ 提取到可嵌入游戏: {game_info['title']} ({game_type})")
            return game_info
            
        except Exception as e:
            logger.error(f"提取单个游戏信息失败: {e}")
            return None
    
    def _extract_category(self, element: BeautifulSoup, base_url: str) -> str:
        """提取游戏分类"""
        # 从元素中查找分类信息
        category_selectors = ['.category', '.genre', '.tag', '[class*="category"]', '[class*="genre"]']
        
        for selector in category_selectors:
            cat_elem = element.select_one(selector)
            if cat_elem:
                cat_text = cat_elem.get_text(strip=True).lower()
                for eng_cat, cn_cat in CATEGORY_MAPPING.items():
                    if eng_cat in cat_text:
                        return cn_cat
        
        # 从URL中推断分类
        url_lower = base_url.lower()
        for eng_cat, cn_cat in CATEGORY_MAPPING.items():
            if eng_cat in url_lower:
                return cn_cat
        
        return '休闲'  # 默认分类
    
    def _determine_game_type(self, game_url: str) -> Tuple[str, Dict]:
        """判断游戏类型（iframe或static），只收集可直接嵌入的游戏"""
        try:
            # 获取游戏页面
            soup = self.fetch_page(game_url)
            if not soup:
                return None, {}
            
            # 1. 优先查找可嵌入的iframe
            iframe_selectors = [
                'iframe[src*="html"]',  # HTML5游戏iframe
                'iframe[src*="game"]',  # 包含game的iframe
                'iframe[src*="play"]',  # 包含play的iframe
                'iframe[src*="embed"]', # 嵌入式iframe
                'iframe[src*=".io"]',   # .io域名的游戏
                'iframe[src*="itch.zone"]', # itch.io的游戏iframe
                'iframe[src*="gamejolt"]',  # GameJolt的iframe
                'iframe[src*="newgrounds"]' # Newgrounds的iframe
            ]
            
            for selector in iframe_selectors:
                iframe = soup.select_one(selector)
                if iframe and iframe.get('src'):
                    iframe_src = urljoin(game_url, iframe['src'])
                    # 验证iframe URL是否可访问
                    if self._validate_iframe_url(iframe_src):
                        logger.info(f"找到可嵌入iframe: {iframe_src}")
                        return 'iframe', {'iframe_url': iframe_src}
            
            # 2. 查找HTML5游戏文件
            game_file_selectors = [
                'a[href$=".html"]',     # HTML文件
                'a[href*="/play"]',     # 包含play的链接
                'a[href*="fullscreen"]', # 全屏游戏链接
                'a[href*="game.html"]', # 游戏HTML文件
                'a[href*="index.html"]' # 主页面文件
            ]
            
            for selector in game_file_selectors:
                for link in soup.select(selector):
                    href = link.get('href', '')
                    if href:
                        full_url = urljoin(game_url, href)
                        # 检查是否是可下载的HTML5游戏
                        if self._is_downloadable_game(full_url):
                            logger.info(f"找到可下载游戏: {full_url}")
                            return 'static', {'static_url': full_url}
            
            # 3. 检查是否有嵌入式游戏容器
            game_containers = soup.select('.game-container, .game-frame, .unity-container, #game-container')
            if game_containers:
                # 查找容器内的脚本或配置
                for container in game_containers:
                    # 查找Unity WebGL游戏
                    unity_script = container.select_one('script[src*="unity"]')
                    if unity_script:
                        logger.info(f"找到Unity WebGL游戏")
                        return 'iframe', {'iframe_url': game_url}
                    
                    # 查找其他嵌入式游戏
                    canvas = container.select_one('canvas')
                    if canvas:
                        logger.info(f"找到Canvas游戏")
                        return 'iframe', {'iframe_url': game_url}
            
            # 4. 如果都没找到，返回None表示不适合收集
            logger.warning(f"未找到可嵌入的游戏内容: {game_url}")
            return None, {}
            
        except Exception as e:
            logger.error(f"判断游戏类型失败 {game_url}: {e}")
            return None, {}
    
    def _validate_iframe_url(self, iframe_url: str) -> bool:
        """验证iframe URL是否可以嵌入"""
        try:
            # 检查URL格式
            parsed = urlparse(iframe_url)
            if not parsed.scheme or not parsed.netloc:
                return False
            
            # 排除不适合嵌入的域名
            blocked_domains = [
                'youtube.com',      # YouTube视频
                'vimeo.com',        # Vimeo视频
                'facebook.com',     # 社交媒体
                'twitter.com',      # 社交媒体
                'instagram.com',    # 社交媒体
                'tiktok.com',       # 短视频
                'ads.',             # 广告
                'analytics.',       # 分析
                'tracking.'         # 跟踪
            ]
            
            for domain in blocked_domains:
                if domain in iframe_url.lower():
                    logger.info(f"跳过不适合嵌入的URL: {iframe_url}")
                    return False
            
            # 发送HEAD请求检查可访问性
            try:
                response = self.session.head(iframe_url, timeout=5, allow_redirects=True)
                # 检查X-Frame-Options头
                frame_options = response.headers.get('X-Frame-Options', '').upper()
                if frame_options in ['DENY', 'SAMEORIGIN']:
                    logger.info(f"URL禁止iframe嵌入: {iframe_url}")
                    return False
                
                # 检查Content-Type
                content_type = response.headers.get('Content-Type', '').lower()
                if 'text/html' in content_type or 'application/' in content_type:
                    return True
                    
            except Exception as e:
                logger.warning(f"验证iframe URL失败: {iframe_url}, {e}")
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"验证iframe URL异常: {iframe_url}, {e}")
            return False
    
    def _is_downloadable_game(self, game_url: str) -> bool:
        """检查是否是可下载的游戏文件"""
        try:
            # 检查文件扩展名
            parsed = urlparse(game_url)
            path = parsed.path.lower()
            
            # 支持的游戏文件类型
            game_extensions = ['.html', '.htm', '.swf', '.unity3d', '.wasm']
            if any(path.endswith(ext) for ext in game_extensions):
                return True
            
            # 检查是否包含游戏相关路径
            game_paths = ['/play', '/game', '/games', 'fullscreen', 'index.html']
            if any(game_path in path for game_path in game_paths):
                # 发送HEAD请求检查文件大小和类型
                try:
                    response = self.session.head(game_url, timeout=5)
                    content_length = response.headers.get('Content-Length')
                    if content_length:
                        size_mb = int(content_length) / (1024 * 1024)
                        # 限制文件大小（小于100MB的游戏文件）
                        if size_mb < 100:
                            return True
                except Exception:
                    pass
            
            return False
            
        except Exception as e:
            logger.error(f"检查可下载游戏失败: {game_url}, {e}")
            return False
    
    def _clean_title(self, title: str) -> str:
        """清理游戏标题"""
        # 移除常见的后缀
        suffixes = [' - Play Online', ' Game', ' Online', ' Free', ' HTML5', ' Browser']
        for suffix in suffixes:
            if title.endswith(suffix):
                title = title[:-len(suffix)]
        
        # 限制长度
        if len(title) > 50:
            title = title[:47] + '...'
        
        return title.strip()
    
    def download_thumbnail(self, thumbnail_url: str, game_id: str) -> str:
        """下载游戏缩略图"""
        try:
            if not thumbnail_url:
                return '/games/thumbnails/default.jpg'
            
            response = self.session.get(thumbnail_url, timeout=10)
            response.raise_for_status()
            
            # 确定文件扩展名
            content_type = response.headers.get('content-type', '')
            if 'jpeg' in content_type or 'jpg' in content_type:
                ext = '.jpg'
            elif 'png' in content_type:
                ext = '.png'
            elif 'gif' in content_type:
                ext = '.gif'
            else:
                ext = '.jpg'
            
            filename = f"{game_id}{ext}"
            filepath = os.path.join(THUMBNAILS_DIR, filename)
            
            with open(filepath, 'wb') as f:
                f.write(response.content)
            
            logger.info(f"下载缩略图成功: {filename}")
            return f'/games/thumbnails/{filename}'
            
        except Exception as e:
            logger.error(f"下载缩略图失败 {thumbnail_url}: {e}")
            return '/games/thumbnails/default.jpg'
    
    def crawl_seed_urls(self) -> List[Dict]:
        """爬取种子URL"""
        all_games = []
        
        for url in SEED_URLS:
            try:
                logger.info(f"正在爬取种子URL: {url}")
                soup = self.fetch_page(url)
                if soup:
                    games = self.extract_game_info(soup, url)
                    all_games.extend(games)
                    logger.info(f"从 {url} 提取到 {len(games)} 个游戏")
                
                # 随机延迟避免被封
                time.sleep(random.uniform(2, 5))
                
            except Exception as e:
                logger.error(f"爬取种子URL失败 {url}: {e}")
                continue
        
        return all_games
    
    def search_games_duckduckgo(self, query: str, max_results: int = 10) -> List[str]:
        """使用DuckDuckGo搜索游戏页面"""
        try:
            search_url = f"https://duckduckgo.com/html/?q={quote(query)}"
            soup = self.fetch_page(search_url)
            if not soup:
                return []
            
            urls = []
            for link in soup.select('.result__a')[:max_results]:
                href = link.get('href')
                if href and href.startswith('http'):
                    urls.append(href)
            
            logger.info(f"DuckDuckGo搜索 '{query}' 找到 {len(urls)} 个结果")
            return urls
            
        except Exception as e:
            logger.error(f"DuckDuckGo搜索失败 '{query}': {e}")
            return []
    
    def process_found_games(self, games: List[Dict]) -> List[Dict]:
        """处理找到的游戏，生成最终的游戏数据"""
        processed_games = []
        
        for i, game in enumerate(games):
            try:
                # 生成游戏ID
                game_id = str(len(self.get_existing_games()) + i + 1)
                
                # 下载缩略图
                thumbnail_path = self.download_thumbnail(game.get('thumbnail_url'), game_id)
                
                # 获取分类ID
                category_id = CATEGORY_ID_MAPPING.get(game['category'], '1')
                
                # 构建游戏数据
                game_data = {
                    'id': game_id,
                    'title': game['title'],
                    'description': game['description'],
                    'category': game['category'],
                    'categoryId': category_id,
                    'thumbnail': thumbnail_path,
                    'path': f'/games/{game_id}',
                    'featured': False,
                    'type': game['type'],
                    'addedAt': datetime.now().strftime('%Y-%m-%d'),
                    'tags': self._generate_tags(game)
                }
                
                # 添加类型特定的数据
                if game['type'] == 'iframe':
                    # 确保iframe URL可以嵌入
                    iframe_url = game['game_data']['iframe_url']
                    if self._validate_iframe_url(iframe_url):
                        game_data['iframeUrl'] = iframe_url
                        logger.info(f"✅ 添加iframe游戏: {game_data['title']} -> {iframe_url}")
                    else:
                        logger.warning(f"❌ 跳过无法嵌入的iframe游戏: {game_data['title']}")
                        continue
                else:
                    # static类型游戏
                    static_url = game['game_data'].get('static_url')
                    if static_url and self._is_downloadable_game(static_url):
                        game_data['staticPath'] = static_url
                        logger.info(f"✅ 添加静态游戏: {game_data['title']} -> {static_url}")
                    else:
                        # 如果没有有效的静态URL，设置为本地路径
                        game_data['staticPath'] = f'/games/{game_id}/index.html'
                        logger.info(f"📁 设置本地路径: {game_data['title']} -> {game_data['staticPath']}")
                
                processed_games.append(game_data)
                
            except Exception as e:
                logger.error(f"处理游戏失败: {e}")
                continue
        
        logger.info(f"🎮 成功处理 {len(processed_games)} 个可嵌入游戏")
        return processed_games
    
    def _generate_tags(self, game: Dict) -> List[str]:
        """为游戏生成标签"""
        tags = [game['category']]
        
        title_lower = game['title'].lower()
        desc_lower = (game.get('description') or '').lower()
        
        # 根据标题和描述添加标签
        tag_keywords = {
            '多人': ['multiplayer', 'multi', '多人', '联机'],
            '单人': ['single', 'solo', '单人'],
            '3D': ['3d', '三维'],
            '2D': ['2d', '二维', 'pixel'],
            '复古': ['retro', 'classic', '经典', '怀旧'],
            '可爱': ['cute', 'kawaii', '可爱', '萌'],
            '困难': ['hard', 'difficult', '困难', '挑战'],
            '简单': ['easy', 'simple', '简单', '轻松']
        }
        
        for tag, keywords in tag_keywords.items():
            if any(keyword in title_lower or keyword in desc_lower for keyword in keywords):
                tags.append(tag)
        
        return tags[:5]  # 限制标签数量
    
    def get_existing_games(self) -> List[Dict]:
        """获取现有的游戏数据"""
        try:
            if not os.path.exists(GAMES_DATA_FILE):
                return []
            
            with open(GAMES_DATA_FILE, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 简单解析现有游戏数据（这里可以改进为更精确的解析）
            import re
            games_match = re.search(r'export const games: Game\[\] = (\[.*?\]);', content, re.DOTALL)
            if games_match:
                # 这里简化处理，实际项目中可能需要更复杂的解析
                return []  # 返回空列表，让新游戏从现有ID继续
            
            return []
            
        except Exception as e:
            logger.error(f"读取现有游戏数据失败: {e}")
            return []
    
    def save_games_to_file(self, new_games: List[Dict]):
        """将新游戏保存到games.ts文件和JSON文件"""
        try:
            # 1. 保存为JSON文件，方便查看和调试
            json_file = os.path.join(PROJECT_ROOT, 'scripts', 'crawled_games.json')
            with open(json_file, 'w', encoding='utf-8') as f:
                json.dump(new_games, f, ensure_ascii=False, indent=2)
            logger.info(f"成功保存 {len(new_games)} 个新游戏到JSON文件: {json_file}")
            
            # 2. 读取现有的games.ts文件
            if os.path.exists(GAMES_DATA_FILE):
                with open(GAMES_DATA_FILE, 'r', encoding='utf-8') as f:
                    content = f.read()
            else:
                content = ""
            
            # 生成新游戏的TypeScript代码
            new_games_code = ""
            for game in new_games:
                # 预处理字符串，避免在f-string中使用反斜杠
                title_escaped = game['title'].replace("'", "\\'")
                desc_escaped = game['description'].replace("'", "\\'")
                
                new_games_code += f"""  {{
    id: '{game['id']}',
    title: '{title_escaped}',
    description: '{desc_escaped}',
    category: '{game['category']}',
    categoryId: '{game['categoryId']}',
    thumbnail: '{game['thumbnail']}',
    path: '{game['path']}',
    featured: {str(game['featured']).lower()},
    type: '{game['type']}',"""
                
                if game['type'] == 'iframe':
                    new_games_code += f"\n    iframeUrl: '{game['iframeUrl']}',"
                else:
                    new_games_code += f"\n    staticPath: '{game['staticPath']}',"
                
                new_games_code += f"""
    addedAt: '{game['addedAt']}',
    tags: {json.dumps(game['tags'], ensure_ascii=False)}
  }},
"""
            
            # 如果文件存在且包含游戏数组，追加新游戏
            if content and 'export const games: Game[] = [' in content:
                # 找到游戏数组结束的位置
                array_end_pos = content.find('];', content.find('export const games: Game[] = ['))
                if array_end_pos != -1:
                    # 在数组结束前插入新游戏
                    new_content = content[:array_end_pos] + new_games_code + content[array_end_pos:]
                else:
                    logger.error("无法找到游戏数组结束位置")
                    new_content = content
            else:
                # 创建新文件
                new_content = f"""import {{ Game, Category }} from '../types';

export const categories: Category[] = [
  {{ id: '1', name: '休闲', description: '简单有趣的休闲游戏，适合所有年龄段玩家', count: 125, slug: 'casual' }},
  {{ id: '2', name: '益智', description: '锻炼大脑的益智游戏，提升思维能力', count: 98, slug: 'puzzle' }},
  {{ id: '3', name: '动作', description: '刺激的动作游戏，考验你的反应速度', count: 84, slug: 'action' }},
  {{ id: '4', name: '卡牌', description: '卡牌和棋牌类游戏，策略与运气的结合', count: 52, slug: 'card' }},
  {{ id: '5', name: '体育', description: '各类体育模拟游戏，感受体育竞技的乐趣', count: 43, slug: 'sports' }},
  {{ id: '6', name: '棋盘', description: '经典的棋盘游戏，考验战略思维', count: 38, slug: 'board' }},
];

export const games: Game[] = [
{new_games_code}];

// 辅助函数
export const getFeaturedGames = (): Game[] => {{
  return games.filter(game => game.featured);
}};

export const getRecentGames = (limit: number = 8): Game[] => {{
  return [...games]
    .sort((a, b) => new Date(b.addedAt).getTime() - new Date(a.addedAt).getTime())
    .slice(0, limit);
}};

export const getGamesByCategory = (categoryId: string): Game[] => {{
  return games.filter(game => game.categoryId === categoryId);
}};

export const getGameById = (id: string): Game | undefined => {{
  return games.find(game => game.id === id);
}};

export const getCategoryById = (id: string): Category | undefined => {{
  return categories.find(category => category.id === id);
}};
"""
            
            # 保存文件
            with open(GAMES_DATA_FILE, 'w', encoding='utf-8') as f:
                f.write(new_content)
            
            logger.info(f"成功追加 {len(new_games)} 个新游戏到 {GAMES_DATA_FILE}")
            
        except Exception as e:
            logger.error(f"保存游戏数据失败: {e}")
    
    def run(self, max_games: int = 50):
        """运行爬虫"""
        logger.info("开始运行游戏爬虫...")
        
        # 1. 爬取种子URL
        logger.info("步骤1: 爬取种子URL...")
        seed_games = self.crawl_seed_urls()
        
        # 2. 搜索引擎搜索
        logger.info("步骤2: 使用搜索引擎搜索...")
        search_games = []
        for query in SEARCH_QUERIES[:5]:  # 限制搜索查询数量
            try:
                urls = self.search_games_duckduckgo(query, 5)
                for url in urls:
                    soup = self.fetch_page(url)
                    if soup:
                        games = self.extract_game_info(soup, url)
                        search_games.extend(games)
                time.sleep(random.uniform(3, 6))
            except Exception as e:
                logger.error(f"搜索查询失败 '{query}': {e}")
                continue
        
        # 3. 合并和去重
        all_games = seed_games + search_games
        unique_games = []
        seen_titles = set()
        
        for game in all_games:
            title_key = game['title'].lower().strip()
            if title_key not in seen_titles:
                seen_titles.add(title_key)
                unique_games.append(game)
        
        logger.info(f"去重后共找到 {len(unique_games)} 个游戏")
        
        # 4. 限制数量并处理
        if len(unique_games) > max_games:
            unique_games = unique_games[:max_games]
        
        logger.info("步骤3: 处理游戏数据...")
        processed_games = self.process_found_games(unique_games)
        
        # 5. 保存到文件
        if processed_games:
            logger.info("步骤4: 保存游戏数据...")
            self.save_games_to_file(processed_games)
            logger.info(f"爬虫运行完成！成功添加 {len(processed_games)} 个游戏")
        else:
            logger.warning("没有找到有效的游戏数据")

    def validate_game_data(self, game_info: Dict) -> bool:
        """验证游戏数据是否有效"""
        try:
            title = game_info.get('title', '').strip()
            description = game_info.get('description', '').strip()
            game_url = game_info.get('game_url', '')
            
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
                'studio',
                'browse games',
                'all games'
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
                'our audience',
                'multiplayer mobile games',
                'digital games and entertainment'
            ]
            
            desc_lower = description.lower()
            if any(keyword in desc_lower for keyword in company_keywords):
                logger.info(f"❌ 跳过公司介绍: {title}")
                return False
            
            # 4. 检查是否是网站首页或分类页
            invalid_url_patterns = [
                '/games$',
                '/games/$',
                'miniclip.com/games$',
                'itch.io/games$',
                'gamejolt.com/games$',
                'newgrounds.com/games$',
                '/browse$',
                '/category$',
                '/tag/$'
            ]
            
            for pattern in invalid_url_patterns:
                if re.search(pattern, game_url, re.IGNORECASE):
                    logger.info(f"❌ 跳过网站首页/分类页: {game_url}")
                    return False
            
            logger.info(f"✅ 游戏数据验证通过: {title}")
            return True
            
        except Exception as e:
            logger.error(f"验证游戏数据失败: {e}")
            return False

def main():
    """主函数"""
    crawler = GameCrawler()
    crawler.run(max_games=30)  # 限制最多爬取30个游戏

if __name__ == '__main__':
    main() 