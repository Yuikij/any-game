#!/usr/bin/env python3
"""
集成游戏爬虫 - 完整版
整合所有优化功能：多平台爬取、API搜索、代理支持、缩略图生成等

使用方法:
    python integrated_game_crawler.py [选项]

选项:
    --mode MODE           爬取模式 (quick/full/api) [默认: full]
    --target TARGET       目标游戏数量 [默认: 50]
    --use-proxy          启用代理
    --generate-thumbnails 生成缩略图
    --api-search         启用API搜索
    --platforms PLATFORMS 指定平台，用逗号分隔 [默认: all]
    --delay DELAY        请求延迟(秒) [默认: 0.5-1.0]
    --workers WORKERS    并发工作线程数 [默认: 3]
    --help               显示帮助信息

示例:
    # 快速模式，爬取30个游戏
    python integrated_game_crawler.py --mode quick --target 30
    
    # 完整模式，使用代理和API搜索
    python integrated_game_crawler.py --mode full --use-proxy --api-search
    
    # 仅从特定平台爬取
    python integrated_game_crawler.py --platforms itch.io,newgrounds
"""

import sys
import os
import json
import time
import random
import asyncio
import aiohttp
import logging
import argparse
import subprocess
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Dict, Set, Any, Optional, Union
from urllib.parse import urljoin, urlparse
from dataclasses import dataclass, asdict
from datetime import datetime

import requests
from bs4 import BeautifulSoup
try:
    from PIL import Image, ImageDraw, ImageFont
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('game_crawler.log', encoding='utf-8')
    ]
)
logger = logging.getLogger(__name__)

@dataclass
class GameInfo:
    """游戏信息数据类"""
    title: str
    url: str
    iframe_url: str
    description: str
    thumbnail: str
    category: str
    tags: List[str]
    platform: str
    score: float = 0.0
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return asdict(self)

class ProxyManager:
    """代理管理器"""
    
    def __init__(self):
        self.proxies = []
        self.current_proxy_index = 0
        self.load_proxies()
    
    def load_proxies(self):
        """加载代理列表"""
        proxy_file = "config/proxies.txt"
        if os.path.exists(proxy_file):
            with open(proxy_file, 'r') as f:
                self.proxies = [line.strip() for line in f if line.strip()]
            logger.info(f"加载了 {len(self.proxies)} 个代理")
    
    def get_proxy(self) -> Optional[Dict[str, str]]:
        """获取代理"""
        if not self.proxies:
            return None
        
        proxy = self.proxies[self.current_proxy_index]
        self.current_proxy_index = (self.current_proxy_index + 1) % len(self.proxies)
        
        return {
            'http': proxy,
            'https': proxy
        }

class APISearcher:
    """API搜索器"""
    
    def __init__(self, use_proxy: bool = False):
        self.proxy_manager = ProxyManager() if use_proxy else None
        self.serp_api_key = self._load_api_key()
    
    def _load_api_key(self) -> Optional[str]:
        """加载API密钥"""
        api_file = "config/api_keys.json"
        if os.path.exists(api_file):
            with open(api_file, 'r') as f:
                keys = json.load(f)
                return keys.get('serp_api_key')
        return None
    
    def search_games_via_api(self, query: str, num_results: int = 20) -> List[GameInfo]:
        """通过API搜索游戏"""
        if not self.serp_api_key:
            logger.warning("SerpAPI密钥未配置")
            return []
        
        try:
            params = {
                'engine': 'google',
                'q': f'{query} HTML5 games site:itch.io OR site:newgrounds.com',
                'api_key': self.serp_api_key,
                'num': num_results
            }
            
            proxies = self.proxy_manager.get_proxy() if self.proxy_manager else None
            response = requests.get('https://serpapi.com/search', params=params, proxies=proxies)
            
            if response.status_code == 200:
                data = response.json()
                games = []
                
                for result in data.get('organic_results', [])[:num_results]:
                    game = GameInfo(
                        title=result.get('title', ''),
                        url=result.get('link', ''),
                        iframe_url=result.get('link', ''),
                        description=result.get('snippet', ''),
                        thumbnail='/games/thumbnails/default.jpg',
                        category='休闲',
                        tags=['API搜索', 'HTML5', 'SerpAPI'],
                        platform='API搜索',
                        score=7.0
                    )
                    games.append(game)
                
                logger.info(f"API搜索找到 {len(games)} 个游戏")
                return games
                
        except Exception as e:
            logger.error(f"API搜索失败: {e}")
        
        return []

class ThumbnailGenerator:
    """缩略图生成器"""
    
    def __init__(self):
        self.colors = [
            [(66, 165, 245), (33, 150, 243)],   # 蓝色
            [(102, 187, 106), (76, 175, 80)],  # 绿色
            [(255, 167, 38), (255, 152, 0)],   # 橙色
            [(171, 71, 188), (156, 39, 176)],  # 紫色
            [(239, 83, 80), (244, 67, 54)],    # 红色
            [(38, 198, 218), (0, 188, 212)],   # 青色
            [(255, 238, 88), (255, 235, 59)],  # 黄色
            [(158, 158, 158), (117, 117, 117)] # 灰色
        ]
    
    def generate_thumbnail(self, title: str, index: int, output_path: str) -> bool:
        """生成单个缩略图"""
        if not PIL_AVAILABLE:
            logger.warning("PIL不可用，跳过缩略图生成")
            return False
        
        try:
            # 创建图像
            width, height = 300, 200
            img = Image.new('RGB', (width, height), 'white')
            draw = ImageDraw.Draw(img)
            
            # 选择颜色
            color_pair = self.colors[index % len(self.colors)]
            
            # 绘制渐变背景
            for y in range(height):
                ratio = y / height
                r = int(color_pair[0][0] * (1 - ratio) + color_pair[1][0] * ratio)
                g = int(color_pair[0][1] * (1 - ratio) + color_pair[1][1] * ratio)
                b = int(color_pair[0][2] * (1 - ratio) + color_pair[1][2] * ratio)
                draw.line([(0, y), (width, y)], fill=(r, g, b))
            
            # 添加几何图案
            pattern_type = index % 4
            if pattern_type == 0:  # 圆形
                draw.ellipse([50, 50, 150, 150], outline='white', width=3)
            elif pattern_type == 1:  # 矩形
                draw.rectangle([50, 50, 150, 150], outline='white', width=3)
            elif pattern_type == 2:  # 三角形
                draw.polygon([(100, 50), (50, 150), (150, 150)], outline='white', width=3)
            else:  # 菱形
                draw.polygon([(100, 50), (150, 100), (100, 150), (50, 100)], outline='white', width=3)
            
            # 添加标题文字
            try:
                font = ImageFont.truetype("arial.ttf", 16)
            except:
                font = ImageFont.load_default()
            
            # 处理标题长度
            if len(title) > 20:
                title = title[:17] + "..."
            
            # 计算文字位置
            bbox = draw.textbbox((0, 0), title, font=font)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]
            text_x = (width - text_width) // 2
            text_y = height - text_height - 20
            
            # 绘制文字阴影
            draw.text((text_x + 1, text_y + 1), title, font=font, fill='black')
            # 绘制文字
            draw.text((text_x, text_y), title, font=font, fill='white')
            
            # 保存图像
            img.save(output_path, 'JPEG', quality=85, optimize=True)
            return True
            
        except Exception as e:
            logger.error(f"生成缩略图失败 {output_path}: {e}")
            return False
    
    def generate_batch_thumbnails(self, count: int) -> int:
        """批量生成缩略图"""
        if not PIL_AVAILABLE:
            logger.warning("PIL不可用，跳过缩略图生成")
            return 0
        
        thumbnail_dir = "public/games/thumbnails"
        os.makedirs(thumbnail_dir, exist_ok=True)
        
        generated = 0
        for i in range(1, count + 1):
            filename = f"auto_game_{i:03d}.jpg"
            output_path = os.path.join(thumbnail_dir, filename)
            
            if not os.path.exists(output_path):
                title = f"Game {i}"
                if self.generate_thumbnail(title, i, output_path):
                    generated += 1
                    if generated % 10 == 0:
                        logger.info(f"已生成 {generated} 个缩略图...")
        
        logger.info(f"批量生成完成，共生成 {generated} 个缩略图")
        return generated

class PlatformCrawler:
    """平台爬虫基类"""
    
    def __init__(self, use_proxy: bool = False, delay_range: tuple = (0.5, 1.0)):
        self.session = requests.Session()
        self.proxy_manager = ProxyManager() if use_proxy else None
        self.delay_range = delay_range
        self.setup_headers()
    
    def setup_headers(self):
        """设置请求头"""
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        })
    
    def get_page(self, url: str) -> Optional[BeautifulSoup]:
        """获取页面内容"""
        try:
            proxies = self.proxy_manager.get_proxy() if self.proxy_manager else None
            response = self.session.get(url, proxies=proxies, timeout=10)
            
            if response.status_code == 200:
                return BeautifulSoup(response.content, 'html.parser')
            else:
                logger.warning(f"HTTP {response.status_code}: {url}")
                return None
                
        except Exception as e:
            logger.error(f"获取页面失败 {url}: {e}")
            return None
    
    def random_delay(self):
        """随机延迟"""
        delay = random.uniform(*self.delay_range)
        time.sleep(delay)

class ItchIoCrawler(PlatformCrawler):
    """itch.io爬虫"""
    
    PLATFORM_NAME = "itch.io"
    SEARCH_URLS = [
        "https://itch.io/games/html5",
        "https://itch.io/games/html5/newest",
        "https://itch.io/games/html5/featured",
        "https://itch.io/games/html5/free"
    ]
    
    def crawl_games(self, max_games: int = 30) -> List[GameInfo]:
        """爬取游戏"""
        all_games = []
        
        for url in self.SEARCH_URLS:
            if len(all_games) >= max_games:
                break
                
            logger.info(f"🎮 爬取 {url}")
            soup = self.get_page(url)
            
            if soup:
                games = self.extract_games_from_page(soup, url)
                all_games.extend(games)
                logger.info(f"✅ 从 {url} 找到 {len(games)} 个游戏")
            
            self.random_delay()
        
        return all_games[:max_games]
    
    def extract_games_from_page(self, soup: BeautifulSoup, page_url: str) -> List[GameInfo]:
        """从页面提取游戏信息"""
        games = []
        
        # 多种选择器尝试
        selectors = [
            '.game_cell',
            '.game_thumb',
            '.game_link',
            'a[href*="/games/"]'
        ]
        
        for selector in selectors:
            game_elements = soup.select(selector)
            if game_elements:
                break
        
        for element in game_elements:
            try:
                game = self.extract_game_info(element, page_url)
                if game and self.validate_game(game):
                    games.append(game)
            except Exception as e:
                logger.debug(f"提取游戏信息失败: {e}")
                continue
        
        return games
    
    def extract_game_info(self, element, page_url: str) -> Optional[GameInfo]:
        """提取单个游戏信息"""
        try:
            # 获取游戏链接
            link_elem = element.find('a') if element.name != 'a' else element
            if not link_elem:
                return None
            
            game_url = urljoin(page_url, link_elem.get('href', ''))
            if not game_url or '/games/' not in game_url:
                return None
            
            # 获取标题
            title_elem = (element.select_one('.title') or 
                         element.select_one('.game_title') or
                         element.select_one('img') or
                         link_elem)
            
            title = ""
            if title_elem:
                if title_elem.name == 'img':
                    title = title_elem.get('alt', title_elem.get('title', ''))
                else:
                    title = title_elem.get_text(strip=True)
            
            if not title:
                return None
            
            # 推断iframe URL
            iframe_url = self.infer_iframe_url(game_url)
            
            # 获取描述
            desc_elem = element.select_one('.game_text, .desc, .description')
            description = desc_elem.get_text(strip=True) if desc_elem else f"来自{self.PLATFORM_NAME}的HTML5游戏"
            
            return GameInfo(
                title=title,
                url=game_url,
                iframe_url=iframe_url,
                description=description,
                thumbnail='/games/thumbnails/default.jpg',
                category='休闲',
                tags=['HTML5', '在线', self.PLATFORM_NAME],
                platform=self.PLATFORM_NAME,
                score=self.calculate_game_score(title, description)
            )
            
        except Exception as e:
            logger.debug(f"提取游戏信息异常: {e}")
            return None
    
    def infer_iframe_url(self, game_url: str) -> str:
        """推断iframe URL"""
        try:
            # 尝试访问游戏页面获取真实iframe
            soup = self.get_page(game_url)
            if soup:
                iframe = soup.select_one('iframe[src*="html-classic.itch.zone"]')
                if iframe:
                    return iframe.get('src')
            
            # 如果无法获取，使用模式推断
            if 'itch.io' in game_url:
                game_id = game_url.split('/')[-1]
                return f"https://html-classic.itch.zone/html/{game_id}/index.html"
            
        except:
            pass
        
        return game_url
    
    def validate_game(self, game: GameInfo) -> bool:
        """验证游戏信息"""
        return (game.title and 
                len(game.title) >= 2 and 
                game.url and 
                game.iframe_url)
    
    def calculate_game_score(self, title: str, description: str) -> float:
        """计算游戏评分"""
        score = 5.0
        
        # 标题质量
        if len(title) > 5:
            score += 1.0
        if len(title) < 50:
            score += 0.5
        
        # 描述质量
        if len(description) > 20:
            score += 1.0
        
        # 关键词奖励
        quality_keywords = ['game', 'play', 'adventure', 'puzzle', 'action']
        if any(keyword in title.lower() or keyword in description.lower() for keyword in quality_keywords):
            score += 0.5
        
        return min(score, 10.0)

class NewgroundsCrawler(PlatformCrawler):
    """Newgrounds爬虫"""
    
    PLATFORM_NAME = "Newgrounds"
    SEARCH_URLS = [
        "https://www.newgrounds.com/games/browse",
        "https://www.newgrounds.com/games/browse/newest",
        "https://www.newgrounds.com/games/browse/featured"
    ]
    
    def crawl_games(self, max_games: int = 20) -> List[GameInfo]:
        """爬取游戏"""
        all_games = []
        
        for url in self.SEARCH_URLS:
            if len(all_games) >= max_games:
                break
                
            logger.info(f"🎮 爬取 {url}")
            soup = self.get_page(url)
            
            if soup:
                games = self.extract_games_from_page(soup, url)
                all_games.extend(games)
                logger.info(f"✅ 从 {url} 找到 {len(games)} 个游戏")
            
            self.random_delay()
        
        return all_games[:max_games]
    
    def extract_games_from_page(self, soup: BeautifulSoup, page_url: str) -> List[GameInfo]:
        """从页面提取游戏信息"""
        games = []
        
        # Newgrounds特定选择器
        selectors = [
            '.item-portalitem',
            '.portal-item',
            'a[href*="/portal/view/"]'
        ]
        
        for selector in selectors:
            game_elements = soup.select(selector)
            if game_elements:
                break
        
        for element in game_elements:
            try:
                game = self.extract_game_info(element, page_url)
                if game and self.validate_game(game):
                    games.append(game)
            except Exception as e:
                logger.debug(f"提取游戏信息失败: {e}")
                continue
        
        return games
    
    def extract_game_info(self, element, page_url: str) -> Optional[GameInfo]:
        """提取单个游戏信息"""
        try:
            # 获取游戏链接
            link_elem = element.find('a') if element.name != 'a' else element
            if not link_elem:
                return None
            
            game_url = urljoin(page_url, link_elem.get('href', ''))
            if not game_url or '/portal/view/' not in game_url:
                return None
            
            # 获取标题
            title_elem = (element.select_one('.item-details h4') or 
                         element.select_one('.title') or
                         element.select_one('img'))
            
            title = ""
            if title_elem:
                if title_elem.name == 'img':
                    title = title_elem.get('alt', title_elem.get('title', ''))
                else:
                    title = title_elem.get_text(strip=True)
            
            if not title:
                return None
            
            # 获取描述
            desc_elem = element.select_one('.item-details p, .description')
            description = desc_elem.get_text(strip=True) if desc_elem else f"来自{self.PLATFORM_NAME}的游戏"
            
            return GameInfo(
                title=title,
                url=game_url,
                iframe_url=game_url,  # Newgrounds通常直接嵌入
                description=description,
                thumbnail='/games/thumbnails/default.jpg',
                category='休闲',
                tags=['Flash', '在线', self.PLATFORM_NAME],
                platform=self.PLATFORM_NAME,
                score=6.0
            )
            
        except Exception as e:
            logger.debug(f"提取游戏信息异常: {e}")
            return None
    
    def validate_game(self, game: GameInfo) -> bool:
        """验证游戏信息"""
        return (game.title and 
                len(game.title) >= 2 and 
                game.url)

class IntegratedGameCrawler:
    """集成游戏爬虫"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.use_proxy = config.get('use_proxy', False)
        self.generate_thumbnails = config.get('generate_thumbnails', True)
        self.api_search = config.get('api_search', False)
        self.delay_range = config.get('delay_range', (0.5, 1.0))
        self.workers = config.get('workers', 3)
        
        # 初始化组件
        self.thumbnail_generator = ThumbnailGenerator()
        self.api_searcher = APISearcher(self.use_proxy) if self.api_search else None
        
        # 初始化平台爬虫
        self.platform_crawlers = {
            'itch.io': ItchIoCrawler(self.use_proxy, self.delay_range),
            'newgrounds': NewgroundsCrawler(self.use_proxy, self.delay_range)
        }
        
        # 加载现有游戏
        self.existing_games = self.load_existing_games()
    
    def load_existing_games(self) -> Set[str]:
        """加载现有游戏标题"""
        existing = set()
        games_file = "src/data/games.ts"
        
        if os.path.exists(games_file):
            with open(games_file, 'r', encoding='utf-8') as f:
                content = f.read()
                # 提取现有游戏标题
                import re
                titles = re.findall(r"title: '([^']+)'", content)
                existing.update(title.lower().strip() for title in titles)
        
        logger.info(f"加载了 {len(existing)} 个现有游戏标题")
        return existing
    
    def is_duplicate(self, game: GameInfo) -> bool:
        """检查是否重复"""
        title_lower = game.title.lower().strip()
        return title_lower in self.existing_games
    
    def crawl_platform(self, platform_name: str, max_games: int) -> List[GameInfo]:
        """爬取单个平台"""
        if platform_name not in self.platform_crawlers:
            logger.warning(f"不支持的平台: {platform_name}")
            return []
        
        logger.info(f"🎮 开始爬取平台: {platform_name}")
        crawler = self.platform_crawlers[platform_name]
        games = crawler.crawl_games(max_games)
        
        # 去重
        unique_games = []
        for game in games:
            if not self.is_duplicate(game):
                unique_games.append(game)
                self.existing_games.add(game.title.lower().strip())
        
        logger.info(f"✅ {platform_name} 完成，找到 {len(unique_games)} 个游戏")
        return unique_games
    
    def crawl_all_platforms(self, target_games: int) -> List[GameInfo]:
        """爬取所有平台"""
        all_games = []
        platforms = self.config.get('platforms', ['itch.io', 'newgrounds'])
        
        if isinstance(platforms, str):
            platforms = [p.strip() for p in platforms.split(',')]
        
        # 计算每个平台的目标数量
        games_per_platform = max(1, target_games // len(platforms))
        
        # 并发爬取
        with ThreadPoolExecutor(max_workers=self.workers) as executor:
            future_to_platform = {
                executor.submit(self.crawl_platform, platform, games_per_platform): platform
                for platform in platforms if platform in self.platform_crawlers
            }
            
            for future in as_completed(future_to_platform):
                platform = future_to_platform[future]
                try:
                    games = future.result()
                    all_games.extend(games)
                    
                    if len(all_games) >= target_games:
                        # 取消其他任务
                        for f in future_to_platform:
                            if not f.done():
                                f.cancel()
                        break
                        
                except Exception as e:
                    logger.error(f"爬取平台 {platform} 失败: {e}")
        
        return all_games[:target_games]
    
    def search_via_api(self, queries: List[str], target_games: int) -> List[GameInfo]:
        """通过API搜索游戏"""
        if not self.api_searcher:
            return []
        
        all_games = []
        games_per_query = max(1, target_games // len(queries))
        
        for query in queries:
            games = self.api_searcher.search_games_via_api(query, games_per_query)
            
            # 去重
            for game in games:
                if not self.is_duplicate(game):
                    all_games.append(game)
                    self.existing_games.add(game.title.lower().strip())
            
            if len(all_games) >= target_games:
                break
        
        return all_games[:target_games]
    
    def generate_game_thumbnails(self, games: List[GameInfo]) -> None:
        """生成游戏缩略图"""
        if not self.generate_thumbnails or not PIL_AVAILABLE:
            return
        
        logger.info("🎨 开始生成缩略图...")
        
        # 生成足够的缩略图
        thumbnail_count = max(50, len(games) + 10)
        generated = self.thumbnail_generator.generate_batch_thumbnails(thumbnail_count)
        
        # 为游戏分配缩略图
        self.assign_thumbnails_to_games(games)
        
        logger.info(f"✅ 缩略图生成完成，共生成 {generated} 个")
    
    def assign_thumbnails_to_games(self, games: List[GameInfo]) -> None:
        """为游戏分配缩略图"""
        thumbnail_dir = "public/games/thumbnails"
        if not os.path.exists(thumbnail_dir):
            return
        
        # 获取可用的自动生成缩略图
        auto_thumbnails = [
            f"/games/thumbnails/{f}" 
            for f in os.listdir(thumbnail_dir) 
            if f.startswith("auto_game_") and f.endswith(".jpg")
        ]
        auto_thumbnails.sort()
        
        # 为默认缩略图的游戏分配新缩略图
        thumbnail_index = 0
        for game in games:
            if game.thumbnail == '/games/thumbnails/default.jpg' and thumbnail_index < len(auto_thumbnails):
                game.thumbnail = auto_thumbnails[thumbnail_index]
                thumbnail_index += 1
    
    def save_games(self, games: List[GameInfo]) -> bool:
        """保存游戏数据"""
        try:
            games_file = "src/data/games.ts"
            
            # 备份原文件
            if os.path.exists(games_file):
                backup_file = f"{games_file}.backup.{int(time.time())}"
                os.rename(games_file, backup_file)
                logger.info(f"📁 已备份原文件: {backup_file}")
            
            # 读取现有数据
            existing_games_data = self.parse_existing_games()
            
            # 合并新游戏
            all_games_data = existing_games_data + [self.convert_to_game_dict(game, len(existing_games_data) + i) for i, game in enumerate(games)]
            
            # 生成新的games.ts文件
            self.write_games_file(all_games_data)
            
            logger.info(f"✅ 成功保存 {len(all_games_data)} 个游戏到 {games_file}")
            return True
            
        except Exception as e:
            logger.error(f"保存游戏数据失败: {e}")
            return False
    
    def parse_existing_games(self) -> List[Dict[str, Any]]:
        """解析现有游戏数据"""
        games_file = "src/data/games.ts"
        if not os.path.exists(games_file):
            return []
        
        try:
            with open(games_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 简单的正则提取（可以改进为更健壮的解析）
            import re
            games_match = re.search(r'export const games: Game\[\] = \[(.*?)\];', content, re.DOTALL)
            if not games_match:
                return []
            
            # 这里可以实现更复杂的解析逻辑
            # 为简化，返回空列表，让新数据追加
            return []
            
        except Exception as e:
            logger.error(f"解析现有游戏数据失败: {e}")
            return []
    
    def convert_to_game_dict(self, game: GameInfo, index: int) -> Dict[str, Any]:
        """转换游戏信息为字典格式"""
        timestamp = int(time.time())
        game_id = f"crawled_{timestamp}_{index}"
        
        return {
            'id': game_id,
            'title': game.title,
            'description': game.description,
            'category': game.category,
            'categoryId': '1',  # 默认为休闲
            'thumbnail': game.thumbnail,
            'path': f'/games/{game_id}',
            'featured': False,
            'type': 'iframe',
            'iframeUrl': game.iframe_url,
            'addedAt': datetime.now().strftime('%Y-%m-%d'),
            'tags': game.tags
        }
    
    def escape_string_for_js(self, text: str) -> str:
        """转义字符串用于JavaScript/TypeScript输出"""
        if not text:
            return text
        
        # 转义特殊字符
        text = text.replace('\\', '\\\\')  # 反斜杠必须首先转义
        text = text.replace("'", "\\'")    # 单引号
        text = text.replace('"', '\\"')    # 双引号  
        text = text.replace('\n', '\\n')   # 换行符
        text = text.replace('\r', '\\r')   # 回车符
        text = text.replace('\t', '\\t')   # 制表符
        
        return text
    
    def write_games_file(self, games_data: List[Dict[str, Any]]) -> None:
        """写入游戏文件"""
        # 统计分类
        category_counts = {}
        for game in games_data:
            category = game['category']
            category_counts[category] = category_counts.get(category, 0) + 1
        
        # 生成文件内容
        content = """import { Game, Category } from '../types';

export const categories: Category[] = [
  { id: '1', name: '休闲', description: '简单有趣的休闲游戏，适合所有年龄段玩家', count: """ + str(category_counts.get('休闲', 0)) + """, slug: 'casual' },
  { id: '2', name: '益智', description: '锻炼大脑的益智游戏，提升思维能力', count: """ + str(category_counts.get('益智', 0)) + """, slug: 'puzzle' },
  { id: '3', name: '动作', description: '刺激的动作游戏，考验你的反应速度', count: """ + str(category_counts.get('动作', 0)) + """, slug: 'action' },
  { id: '4', name: '卡牌', description: '卡牌和棋牌类游戏，策略与运气的结合', count: """ + str(category_counts.get('卡牌', 0)) + """, slug: 'card' },
  { id: '5', name: '体育', description: '各类体育模拟游戏，感受体育竞技的乐趣', count: """ + str(category_counts.get('体育', 0)) + """, slug: 'sports' },
  { id: '6', name: '棋盘', description: '经典的棋盘游戏，考验战略思维', count: """ + str(category_counts.get('棋盘', 0)) + """, slug: 'board' },
];

export const games: Game[] = [
"""
        
                                  # 添加游戏数据
        for i, game in enumerate(games_data):
            # 安全处理字符串，转义单引号和其他特殊字符
            title = self.escape_string_for_js(game['title'])
            description = self.escape_string_for_js(game['description'])
            category = self.escape_string_for_js(game['category'])
            thumbnail = self.escape_string_for_js(game['thumbnail'])
            path = self.escape_string_for_js(game['path'])
            iframe_url = self.escape_string_for_js(game['iframeUrl'])
            
            content += f"""  {{
    id: '{game['id']}',
    title: '{title}',
    description: '{description}',
    category: '{category}',
    categoryId: '{game['categoryId']}',
    thumbnail: '{thumbnail}',
    path: '{path}',
    featured: {str(game['featured']).lower()},
    type: '{game['type']}',
    iframeUrl: '{iframe_url}',
    addedAt: '{game['addedAt']}',
    tags: {json.dumps(game['tags'], ensure_ascii=False)}
  }}"""
            
            if i < len(games_data) - 1:
                content += ","
            content += "\n"
        
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
        
        # 写入文件
        with open("src/data/games.ts", 'w', encoding='utf-8') as f:
            f.write(content)
    
    def run(self, mode: str = 'full', target_games: int = 50) -> bool:
        """运行爬虫"""
        logger.info(f"🚀 启动集成游戏爬虫 - 模式: {mode}, 目标: {target_games} 个游戏")
        
        all_games = []
        
        try:
            # 根据模式执行不同策略
            if mode == 'quick':
                # 快速模式：主要从itch.io爬取
                all_games = self.crawl_platform('itch.io', target_games)
                
            elif mode == 'api':
                # API模式：主要通过API搜索
                queries = ['HTML5 games', 'browser games', 'online games', 'web games']
                all_games = self.search_via_api(queries, target_games)
                
            elif mode == 'full':
                # 完整模式：多平台 + API搜索
                platform_games = target_games * 2 // 3  # 2/3 来自平台爬取
                api_games = target_games - len(all_games)  # 剩余来自API
                
                # 平台爬取
                all_games.extend(self.crawl_all_platforms(platform_games))
                
                # API搜索补充
                if self.api_search and len(all_games) < target_games:
                    queries = ['HTML5 games', 'browser games']
                    api_results = self.search_via_api(queries, api_games)
                    all_games.extend(api_results)
            
            else:
                logger.error(f"不支持的模式: {mode}")
                return False
            
            # 去重
            unique_games = []
            seen_titles = set()
            for game in all_games:
                title_lower = game.title.lower().strip()
                if title_lower not in seen_titles:
                    unique_games.append(game)
                    seen_titles.add(title_lower)
            
            logger.info(f"🎯 去重后找到 {len(unique_games)} 个唯一游戏")
            
            # 生成缩略图
            if self.generate_thumbnails:
                self.generate_game_thumbnails(unique_games)
            
            # 保存游戏
            if unique_games:
                success = self.save_games(unique_games)
                if success:
                    self.print_summary(unique_games)
                    return True
            else:
                logger.warning("没有找到新游戏")
            
        except Exception as e:
            logger.error(f"爬虫执行失败: {e}", exc_info=True)
        
        return False
    
    def print_summary(self, games: List[GameInfo]) -> None:
        """打印摘要"""
        logger.info("📊 爬取统计:")
        
        # 按平台统计
        platform_stats = {}
        for game in games:
            platform = game.platform
            platform_stats[platform] = platform_stats.get(platform, 0) + 1
        
        for platform, count in platform_stats.items():
            logger.info(f"  🎮 {platform}: {count} 个游戏")
        
        # 缩略图统计
        thumbnail_stats = {
            'default': 0,
            'auto': 0,
            'custom': 0
        }
        
        for game in games:
            if 'default.jpg' in game.thumbnail:
                thumbnail_stats['default'] += 1
            elif 'auto_game_' in game.thumbnail:
                thumbnail_stats['auto'] += 1
            else:
                thumbnail_stats['custom'] += 1
        
        logger.info(f"  🖼️ 自定义缩略图: {thumbnail_stats['custom']}/{len(games)} 个")
        logger.info("🎉 集成爬虫执行完成！")

def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description='集成游戏爬虫 - 完整版',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用示例:
  %(prog)s --mode quick --target 30
  %(prog)s --mode full --use-proxy --api-search
  %(prog)s --platforms itch.io,newgrounds --generate-thumbnails
        """
    )
    
    parser.add_argument('--mode', choices=['quick', 'full', 'api'], default='full',
                        help='爬取模式 (默认: full)')
    parser.add_argument('--target', type=int, default=50,
                        help='目标游戏数量 (默认: 50)')
    parser.add_argument('--use-proxy', action='store_true',
                        help='启用代理')
    parser.add_argument('--generate-thumbnails', action='store_true', default=True,
                        help='生成缩略图 (默认启用)')
    parser.add_argument('--api-search', action='store_true',
                        help='启用API搜索')
    parser.add_argument('--platforms', default='itch.io,newgrounds',
                        help='指定平台，用逗号分隔 (默认: itch.io,newgrounds)')
    parser.add_argument('--delay', default='0.5-1.0',
                        help='请求延迟范围(秒) (默认: 0.5-1.0)')
    parser.add_argument('--workers', type=int, default=3,
                        help='并发工作线程数 (默认: 3)')
    
    args = parser.parse_args()
    
    # 解析延迟参数
    delay_parts = args.delay.split('-')
    if len(delay_parts) == 2:
        delay_range = (float(delay_parts[0]), float(delay_parts[1]))
    else:
        delay_range = (0.5, 1.0)
    
    # 构建配置
    config = {
        'use_proxy': args.use_proxy,
        'generate_thumbnails': args.generate_thumbnails,
        'api_search': args.api_search,
        'platforms': args.platforms,
        'delay_range': delay_range,
        'workers': args.workers
    }
    
    # 创建并运行爬虫
    crawler = IntegratedGameCrawler(config)
    success = crawler.run(args.mode, args.target)
    
    if success:
        print("✅ 爬虫执行成功！")
        sys.exit(0)
    else:
        print("❌ 爬虫执行失败！")
        sys.exit(1)

if __name__ == "__main__":
    main() 