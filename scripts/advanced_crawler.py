#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
高级游戏爬虫 - 结合API搜索和本地下载
优先下载HTML5游戏文件到本地，其次考虑iframe嵌入
"""

import requests
from bs4 import BeautifulSoup
import json
import random
import time
import os
import zipfile
import shutil
import logging
from urllib.parse import urljoin, urlparse
from datetime import datetime
from typing import List, Dict, Optional

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('advanced_crawler.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# 项目配置
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GAMES_DATA_FILE = os.path.join(PROJECT_ROOT, 'src', 'data', 'games.ts')
LOCAL_GAMES_DIR = os.path.join(PROJECT_ROOT, 'public', 'games')
THUMBNAILS_DIR = os.path.join(PROJECT_ROOT, 'public', 'games', 'thumbnails')

# API配置（可选）
SERPAPI_KEY = os.getenv('SERPAPI_KEY', '')
GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY', '')
GOOGLE_CX = os.getenv('GOOGLE_CX', '')

# 模拟浏览器头
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
    'Accept-Encoding': 'gzip, deflate, br',
    'Connection': 'keep-alive'
}

# 高质量HTML5游戏平台
PREMIUM_GAME_SITES = [
    {
        'name': 'itch.io HTML5',
        'base_url': 'https://itch.io',
        'search_url': 'https://itch.io/games/html5',
        'game_selector': '.game_cell',
        'title_selector': '.title',
        'download_selector': '.download_btn, .play_btn',
        'priority': 1  # 最高优先级
    },
    {
        'name': 'GameJolt HTML5',
        'base_url': 'https://gamejolt.com',
        'search_url': 'https://gamejolt.com/games/best/html',
        'game_selector': '.game-listing-item',
        'title_selector': '.game-title',
        'download_selector': '.download-button',
        'priority': 2
    },
    {
        'name': 'OpenGameArt',
        'base_url': 'https://opengameart.org',
        'search_url': 'https://opengameart.org/art-search-advanced?keys=&field_art_type_tid%5B%5D=9',
        'game_selector': '.node',
        'title_selector': '.title',
        'download_selector': '.download',
        'priority': 3
    }
]

# 可嵌入域名白名单
EMBEDDABLE_DOMAINS = [
    'html-classic.itch.zone',
    'v6p9d9t4.ssl.hwcdn.net',
    'uploads.ungrounded.net',
    'gamejolt.net',
    'crazygames.com/embed',
    'poki.com/embed'
]

class AdvancedGameCrawler:
    """高级游戏爬虫类"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update(HEADERS)
        self.downloaded_games = []
        self.iframe_games = []
        
        # 确保目录存在
        os.makedirs(LOCAL_GAMES_DIR, exist_ok=True)
        os.makedirs(THUMBNAILS_DIR, exist_ok=True)
    
    def search_with_api(self, query: str, max_results: int = 10) -> List[str]:
        """使用API搜索游戏（如果配置了API密钥）"""
        urls = []
        
        # 尝试使用SerpAPI
        if SERPAPI_KEY:
            try:
                from serpapi import GoogleSearch
                params = {
                    'q': query,
                    'api_key': SERPAPI_KEY,
                    'num': max_results
                }
                search = GoogleSearch(params)
                results = search.get_dict()
                api_urls = [result.get('link') for result in results.get('organic_results', [])]
                urls.extend(api_urls)
                logger.info(f"SerpAPI找到 {len(api_urls)} 个结果")
            except Exception as e:
                logger.warning(f"SerpAPI搜索失败: {e}")
        
        # 尝试使用Google Custom Search API
        if GOOGLE_API_KEY and GOOGLE_CX:
            try:
                params = {
                    'key': GOOGLE_API_KEY,
                    'cx': GOOGLE_CX,
                    'q': query,
                    'num': max_results
                }
                response = self.session.get('https://www.googleapis.com/customsearch/v1', params=params)
                response.raise_for_status()
                data = response.json()
                google_urls = [item.get('link') for item in data.get('items', [])]
                urls.extend(google_urls)
                logger.info(f"Google API找到 {len(google_urls)} 个结果")
            except Exception as e:
                logger.warning(f"Google API搜索失败: {e}")
        
        return list(set(urls))  # 去重
    
    def download_html5_game(self, game_url: str, game_title: str, game_id: str) -> Optional[Dict]:
        """下载HTML5游戏到本地"""
        try:
            logger.info(f"尝试下载游戏: {game_title}")
            
            # 获取游戏页面
            response = self.session.get(game_url, timeout=15)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # 查找下载链接
            download_links = []
            
            # 查找直接的HTML5游戏文件
            for link in soup.select('a[href]'):
                href = link.get('href', '')
                if any(ext in href.lower() for ext in ['.html', '.htm', 'index.html', 'game.html']):
                    download_links.append(urljoin(game_url, href))
            
            # 查找ZIP文件（可能包含HTML5游戏）
            for link in soup.select('a[href*=".zip"], a[href*="download"]'):
                href = link.get('href', '')
                if href:
                    download_links.append(urljoin(game_url, href))
            
            # 尝试下载游戏文件
            for download_url in download_links[:3]:  # 限制尝试次数
                try:
                    game_data = self._download_game_file(download_url, game_id, game_title)
                    if game_data:
                        logger.info(f"✅ 成功下载游戏: {game_title}")
                        return game_data
                except Exception as e:
                    logger.warning(f"下载失败 {download_url}: {e}")
                    continue
            
            logger.warning(f"❌ 无法下载游戏: {game_title}")
            return None
            
        except Exception as e:
            logger.error(f"下载游戏失败 {game_title}: {e}")
            return None
    
    def _download_game_file(self, download_url: str, game_id: str, game_title: str) -> Optional[Dict]:
        """下载具体的游戏文件"""
        try:
            response = self.session.get(download_url, timeout=30, stream=True)
            response.raise_for_status()
            
            content_type = response.headers.get('Content-Type', '').lower()
            content_length = int(response.headers.get('Content-Length', 0))
            
            # 限制文件大小（50MB）
            if content_length > 50 * 1024 * 1024:
                logger.warning(f"文件过大，跳过: {download_url}")
                return None
            
            game_dir = os.path.join(LOCAL_GAMES_DIR, game_id)
            os.makedirs(game_dir, exist_ok=True)
            
            if 'zip' in content_type or download_url.endswith('.zip'):
                # 处理ZIP文件
                zip_path = os.path.join(game_dir, 'game.zip')
                with open(zip_path, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        f.write(chunk)
                
                # 解压ZIP文件
                with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                    zip_ref.extractall(game_dir)
                
                os.remove(zip_path)  # 删除ZIP文件
                
                # 查找主HTML文件
                html_files = []
                for root, dirs, files in os.walk(game_dir):
                    for file in files:
                        if file.endswith(('.html', '.htm')):
                            html_files.append(os.path.join(root, file))
                
                if html_files:
                    # 选择最可能的主文件
                    main_file = self._find_main_html(html_files)
                    relative_path = os.path.relpath(main_file, LOCAL_GAMES_DIR)
                    
                    return {
                        'type': 'static',
                        'staticPath': f'/games/{relative_path.replace(os.sep, "/")}',
                        'local_path': main_file
                    }
            
            elif 'html' in content_type or download_url.endswith(('.html', '.htm')):
                # 处理HTML文件
                html_path = os.path.join(game_dir, 'index.html')
                with open(html_path, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        f.write(chunk)
                
                return {
                    'type': 'static',
                    'staticPath': f'/games/{game_id}/index.html',
                    'local_path': html_path
                }
            
            return None
            
        except Exception as e:
            logger.error(f"下载文件失败: {e}")
            return None
    
    def _find_main_html(self, html_files: List[str]) -> str:
        """从HTML文件列表中找到主文件"""
        # 优先级：index.html > game.html > main.html > 其他
        priority_names = ['index.html', 'game.html', 'main.html', 'start.html']
        
        for priority_name in priority_names:
            for html_file in html_files:
                if os.path.basename(html_file).lower() == priority_name:
                    return html_file
        
        # 如果没找到优先文件，返回第一个
        return html_files[0] if html_files else None
    
    def find_iframe_games(self, game_url: str, game_title: str) -> Optional[Dict]:
        """查找可嵌入的iframe游戏"""
        try:
            response = self.session.get(game_url, timeout=10)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # 查找iframe
            iframes = soup.select('iframe[src]')
            for iframe in iframes:
                iframe_src = iframe.get('src')
                if iframe_src:
                    iframe_url = urljoin(game_url, iframe_src)
                    
                    # 检查是否是可嵌入的域名
                    parsed = urlparse(iframe_url)
                    if any(domain in parsed.netloc for domain in EMBEDDABLE_DOMAINS):
                        logger.info(f"✅ 找到可嵌入游戏: {game_title}")
                        return {
                            'type': 'iframe',
                            'iframeUrl': iframe_url
                        }
            
            return None
            
        except Exception as e:
            logger.error(f"查找iframe游戏失败: {e}")
            return None
    
    def crawl_premium_sites(self, max_games_per_site: int = 10) -> List[Dict]:
        """爬取高质量游戏网站"""
        all_games = []
        
        for site in PREMIUM_GAME_SITES:
            try:
                logger.info(f"正在爬取: {site['name']}")
                response = self.session.get(site['search_url'], timeout=15)
                response.raise_for_status()
                soup = BeautifulSoup(response.text, 'html.parser')
                
                game_elements = soup.select(site['game_selector'])[:max_games_per_site]
                
                for i, element in enumerate(game_elements):
                    try:
                        # 提取游戏信息
                        title_elem = element.select_one(site['title_selector'])
                        if not title_elem:
                            continue
                        
                        title = title_elem.get_text(strip=True)
                        if len(title) < 3:
                            continue
                        
                        # 获取游戏链接
                        link_elem = element.select_one('a[href]')
                        if not link_elem:
                            continue
                        
                        game_url = urljoin(site['base_url'], link_elem['href'])
                        game_id = f"{site['name'].lower().replace(' ', '_')}_{i+1}"
                        
                        # 优先尝试下载到本地
                        game_data = self.download_html5_game(game_url, title, game_id)
                        
                        # 如果下载失败，尝试iframe
                        if not game_data:
                            game_data = self.find_iframe_games(game_url, title)
                        
                        if game_data:
                            game_info = {
                                'id': game_id,
                                'title': title,
                                'description': f"来自{site['name']}的HTML5游戏",
                                'category': '休闲',
                                'categoryId': '1',
                                'thumbnail': '/games/thumbnails/default.jpg',
                                'path': f'/games/{game_id}',
                                'featured': False,
                                'addedAt': datetime.now().strftime('%Y-%m-%d'),
                                'tags': ['HTML5', '在线'],
                                'source': site['name'],
                                **game_data
                            }
                            all_games.append(game_info)
                            
                            if game_data['type'] == 'static':
                                self.downloaded_games.append(game_info)
                            else:
                                self.iframe_games.append(game_info)
                        
                        time.sleep(random.uniform(2, 4))  # 避免请求过快
                        
                    except Exception as e:
                        logger.error(f"处理游戏失败: {e}")
                        continue
                
                time.sleep(random.uniform(5, 8))  # 网站间延迟
                
            except Exception as e:
                logger.error(f"爬取网站失败 {site['name']}: {e}")
                continue
        
        return all_games
    
    def save_games_data(self, games: List[Dict]):
        """保存游戏数据到文件"""
        try:
            # 保存为JSON文件
            json_file = os.path.join(PROJECT_ROOT, 'scripts', 'advanced_games.json')
            with open(json_file, 'w', encoding='utf-8') as f:
                json.dump(games, f, ensure_ascii=False, indent=2)
            
            logger.info(f"✅ 保存 {len(games)} 个游戏到 {json_file}")
            logger.info(f"📁 本地游戏: {len(self.downloaded_games)} 个")
            logger.info(f"🌐 iframe游戏: {len(self.iframe_games)} 个")
            
        except Exception as e:
            logger.error(f"保存游戏数据失败: {e}")
    
    def run(self, max_games: int = 30):
        """运行高级爬虫"""
        logger.info("🚀 开始运行高级游戏爬虫...")
        logger.info("💡 优先下载HTML5游戏到本地，其次考虑iframe嵌入")
        
        # 1. 爬取高质量游戏网站
        games = self.crawl_premium_sites(max_games_per_site=max_games//len(PREMIUM_GAME_SITES))
        
        # 2. 如果配置了API，进行额外搜索
        if SERPAPI_KEY or (GOOGLE_API_KEY and GOOGLE_CX):
            logger.info("🔍 使用API进行额外搜索...")
            api_queries = [
                'HTML5 games download',
                'browser games source code',
                'free HTML5 games'
            ]
            
            for query in api_queries:
                try:
                    urls = self.search_with_api(query, 5)
                    # 处理API搜索结果...
                    time.sleep(random.uniform(3, 5))
                except Exception as e:
                    logger.error(f"API搜索失败: {e}")
        
        # 3. 保存结果
        if games:
            self.save_games_data(games)
            logger.info(f"✅ 高级爬虫完成！总共处理 {len(games)} 个游戏")
        else:
            logger.warning("❌ 没有找到有效的游戏")

def main():
    """主函数"""
    crawler = AdvancedGameCrawler()
    crawler.run(max_games=20)

if __name__ == '__main__':
    main() 