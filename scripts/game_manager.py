#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
游戏管理器 - 统一的游戏数据管理工具
包含：爬虫、清理、去重、修复、下载等所有核心功能

🆕 新功能：智能选择器检测
- 现在可以自动检测游戏网站的CSS选择器
- 添加新平台只需要提供基本URL信息
- 测试工具：python test_selector_detection.py <网站URL>

🔧 配置方法：
1. 直接修改配置文件（推荐）：
   编辑 scripts/config.py 中的 Config 类，如 USE_PROXY = True

2. 环境变量配置：
   export USE_PROXY=true PROXY_HOST=127.0.0.1 PROXY_PORT=7890

3. 命令行参数：
   python game_manager.py --use-proxy --strict-whitelist

📋 查看当前配置：python show_config.py

📝 重要配置项：
- USE_PROXY: 是否启用代理
- STRICT_WHITELIST: 是否启用严格白名单模式
- SERPAPI_KEY/GOOGLE_API_KEY: API密钥（可选）

详细配置说明请查看 WHITELIST_MODES.md
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
import re
from urllib.parse import urljoin, urlparse
from datetime import datetime
from typing import List, Dict, Optional, Any
import argparse
from http.client import RemoteDisconnected
from requests.exceptions import RequestException, ConnectionError, Timeout
from tenacity import retry, stop_after_attempt, wait_fixed, retry_if_exception_type

# 尝试导入SerpAPI
try:
    import serpapi
    SERPAPI_AVAILABLE = True
except ImportError:
    SERPAPI_AVAILABLE = False
    print("⚠️ SerpAPI库未安装，将使用基础API调用")

# 尝试导入PIL（缩略图生成）
try:
    from PIL import Image, ImageDraw, ImageFont
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False
    print("⚠️ PIL库未安装，缩略图生成功能不可用")

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('game_manager.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# ========================================================================================
# 🔧 核心配置区域 - 集成所有配置
# ========================================================================================

class Config:
    """游戏管理器配置类 - 集中管理所有配置项"""
    
    # 🌐 代理配置
    USE_PROXY = True         # 📝 改为 True 启用代理
    PROXY_HOST = '127.0.0.1'  # 📝 代理服务器地址
    PROXY_PORT = '7890'       # 📝 代理服务器端口
    
    # 🛡️ 白名单配置
    STRICT_WHITELIST = False  # 📝 改为 True 启用严格白名单模式
    
    # 🎯 爬虫配置
    MAX_GAMES_DEFAULT = 10    # 📝 默认爬取游戏数量
    CRAWL_DELAY_MIN = 2.0     # 📝 最小延迟（秒）
    CRAWL_DELAY_MAX = 5.0     # 📝 最大延迟（秒）
    REQUEST_TIMEOUT = 15      # 📝 请求超时时间（秒）
    RETRY_ATTEMPTS = 3        # 📝 重试次数
    
    # 🚦 特定平台延迟配置（避免429错误）
    PLATFORM_DELAYS = {
        'itch.io': (4.0, 8.0),
        'gamejolt.com': (3.0, 6.0),
        'newgrounds.com': (2.0, 4.0),
        'crazygames.com': (3.0, 5.0),
        'gamedistribution.com': (2.0, 4.0),
        'scratch.mit.edu': (5.0, 8.0),  # Scratch需要更长延迟
        'miniplay.com': (3.0, 6.0),
        'default': (2.0, 5.0)
    }
    
    # 🔍 API配置
    SERPAPI_KEY = ""        # 📝 在这里设置你的SerpAPI密钥
    GOOGLE_API_KEY = ""     # 📝 在这里设置你的Google API密钥
    GOOGLE_CX = ""          # 📝 在这里设置你的Google Custom Search Engine ID
    
    # 📁 路径配置
    PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    GAMES_DATA_FILE = os.path.join(PROJECT_ROOT, 'src', 'data', 'games.ts')
    LOCAL_GAMES_DIR = os.path.join(PROJECT_ROOT, 'public', 'games')
    THUMBNAILS_DIR = os.path.join(PROJECT_ROOT, 'public', 'games', 'thumbnails')
    
    # 🎮 游戏验证配置
    GAME_URL_SCORE_THRESHOLD = 50  # 📝 智能验证的分数阈值
    
    @classmethod
    def load_from_env(cls):
        """从环境变量加载配置（可覆盖默认值）"""
        cls.USE_PROXY = os.getenv('USE_PROXY', str(cls.USE_PROXY)).lower() == 'true'
        cls.PROXY_HOST = os.getenv('PROXY_HOST', cls.PROXY_HOST)
        cls.PROXY_PORT = os.getenv('PROXY_PORT', cls.PROXY_PORT)
        cls.STRICT_WHITELIST = os.getenv('STRICT_WHITELIST', str(cls.STRICT_WHITELIST)).lower() == 'true'
        
        # API密钥优先从环境变量读取
        cls.SERPAPI_KEY = os.getenv('SERPAPI_KEY', cls.SERPAPI_KEY)
        cls.GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY', cls.GOOGLE_API_KEY)
        cls.GOOGLE_CX = os.getenv('GOOGLE_CX', cls.GOOGLE_CX)
        
        # 数值配置
        try:
            cls.MAX_GAMES_DEFAULT = int(os.getenv('MAX_GAMES_DEFAULT', str(cls.MAX_GAMES_DEFAULT)))
            cls.CRAWL_DELAY_MIN = float(os.getenv('CRAWL_DELAY_MIN', str(cls.CRAWL_DELAY_MIN)))
            cls.CRAWL_DELAY_MAX = float(os.getenv('CRAWL_DELAY_MAX', str(cls.CRAWL_DELAY_MAX)))
            cls.REQUEST_TIMEOUT = int(os.getenv('REQUEST_TIMEOUT', str(cls.REQUEST_TIMEOUT)))
            cls.RETRY_ATTEMPTS = int(os.getenv('RETRY_ATTEMPTS', str(cls.RETRY_ATTEMPTS)))
            cls.GAME_URL_SCORE_THRESHOLD = int(os.getenv('GAME_URL_SCORE_THRESHOLD', str(cls.GAME_URL_SCORE_THRESHOLD)))
        except ValueError:
            pass  # 使用默认值
    
    @classmethod
    def update_from_args(cls, args):
        """从命令行参数更新配置"""
        if hasattr(args, 'use_proxy') and args.use_proxy:
            cls.USE_PROXY = True
        if hasattr(args, 'strict_whitelist') and args.strict_whitelist:
            cls.STRICT_WHITELIST = True
        if hasattr(args, 'max_games') and args.max_games:
            cls.MAX_GAMES_DEFAULT = args.max_games
    
    @classmethod
    def print_status(cls):
        """打印当前配置状态"""
        print("🔧 当前配置状态:")
        print(f"  代理模式: {'✅ 启用' if cls.USE_PROXY else '❌ 禁用'}")
        if cls.USE_PROXY:
            print(f"  代理地址: {cls.PROXY_HOST}:{cls.PROXY_PORT}")
        print(f"  白名单模式: {'🔒 严格模式' if cls.STRICT_WHITELIST else '🤖 智能模式'}")
        print(f"  默认爬取数量: {cls.MAX_GAMES_DEFAULT}")
        print(f"  API配置: SerpAPI={'✅' if cls.SERPAPI_KEY else '❌'}, Google={'✅' if cls.GOOGLE_API_KEY else '❌'}")
        # 检查PIL是否可用
        try:
            from PIL import Image, ImageDraw, ImageFont
            pil_available = True
        except ImportError:
            pil_available = False
        print(f"  缩略图生成: {'✅ 可用' if pil_available else '❌ 不可用'}")

# 初始化配置
Config.load_from_env()

# 项目配置
PROJECT_ROOT = Config.PROJECT_ROOT
GAMES_DATA_FILE = Config.GAMES_DATA_FILE
LOCAL_GAMES_DIR = Config.LOCAL_GAMES_DIR
THUMBNAILS_DIR = Config.THUMBNAILS_DIR

# 导入共享配置
USE_PROXY = Config.USE_PROXY
PROXY_HOST = Config.PROXY_HOST
PROXY_PORT = Config.PROXY_PORT
STRICT_WHITELIST = Config.STRICT_WHITELIST
SERPAPI_KEY = Config.SERPAPI_KEY
GOOGLE_API_KEY = Config.GOOGLE_API_KEY
GOOGLE_CX = Config.GOOGLE_CX



# 导入共享配置（已集成到本文件中）

# 全局代理设置（类似Java的-Dhttps.proxyHost）
def setup_global_proxy():
    """设置全局代理，类似Java的JVM参数"""
    if USE_PROXY:
        proxy_url = f"http://{PROXY_HOST}:{PROXY_PORT}"
        
        # 方法1：环境变量（对所有HTTP库生效）
        os.environ['HTTP_PROXY'] = proxy_url
        os.environ['HTTPS_PROXY'] = proxy_url
        os.environ['http_proxy'] = proxy_url
        os.environ['https_proxy'] = proxy_url
        
        # 方法2：为requests库设置全局默认代理
        import requests
        requests.adapters.DEFAULT_RETRIES = 3
        
        # 测试代理是否可用
        try:
            test_response = requests.get('https://httpbin.org/ip', 
                                       proxies={'http': proxy_url, 'https': proxy_url}, 
                                       timeout=5)
            if test_response.status_code == 200:
                logger.info(f"✅ 代理测试成功: {PROXY_HOST}:{PROXY_PORT}")
                return True
            else:
                logger.warning(f"⚠️ 代理测试失败: HTTP {test_response.status_code}")
                return False
        except Exception as e:
            logger.warning(f"⚠️ 代理不可用: {e}")
            return False
    return False

# 初始化全局代理
PROXY_AVAILABLE = setup_global_proxy() if USE_PROXY else False

# 模拟浏览器头（轮换使用）
USER_AGENTS = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
]

def get_random_headers():
    """获取随机的请求头"""
    return {
        'User-Agent': random.choice(USER_AGENTS),
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
        'Accept-Encoding': 'gzip, deflate, br',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'none',
        'Cache-Control': 'max-age=0'
    }

# 高质量HTML5游戏平台 - 扩展版
PREMIUM_GAME_SITES = [
    {
        'name': 'itch.io HTML5',
        'base_url': 'https://itch.io',
        'search_url': 'https://itch.io/games/html5',
        'game_selector': '.game_cell',
        'title_selector': '.title',
        'priority': 1
    },
    {
        'name': 'GameJolt',
        'base_url': 'https://gamejolt.com',
        'search_url': 'https://gamejolt.com/games',
        'priority': 2
    },
    {
        'name': 'CrazyGames New',
        'base_url': 'https://www.crazygames.com',
        'search_url': 'https://www.crazygames.com/new',
        'game_selector': '.game-tile, .game-item, [data-game-id]',
        'title_selector': '.game-title, .title, h3, h4',
        'priority': 3
    },
    {
        'name': 'GameDistribution',
        'base_url': 'https://gamedistribution.com',
        'search_url': 'https://gamedistribution.com/games/',
        'game_selector': '.game-item, .game-card, .grid-item',
        'title_selector': '.game-title, .title, h3',
        'priority': 4
    },
    {
        'name': 'Scratch MIT',
        'base_url': 'https://scratch.mit.edu',
        'search_url': 'https://scratch.mit.edu/explore/projects/all/',
        'game_selector': '.thumbnail, .gallery-item',
        'title_selector': '.thumbnail-title, .title',
        'priority': 5
    },
    {
        'name': 'Miniplay',
        'base_url': 'https://www.miniplay.com',
        'search_url': 'https://www.miniplay.com/most-played',
        'game_selector': '.game-item, .game-box, .grid-item',
        'title_selector': '.game-title, .title, h3',
        'priority': 6
    }
]

# 可嵌入域名白名单（扩展版，包含新网站）
EMBEDDABLE_DOMAINS = [
    # itch.io 游戏托管域名
    'html-classic.itch.zone',
    'v6p9d9t4.ssl.hwcdn.net',
    'kdata.itch.zone',
    'assets.itch.zone',
    
    # Newgrounds 游戏域名
    'uploads.ungrounded.net',
    'www.newgrounds.com/portal/view',
    'newgrounds.com/portal',
    
    # GameJolt 游戏域名
    'gamejolt.net',
    'cdn.gamejolt.net',
    
    # CrazyGames域名
    'crazygames.com/embed',
    'embed.crazygames.com',
    'crazygames.com/new',
    'files.crazygames.com',
    'assets.crazygames.com',
    
    # GameDistribution域名
    'gamedistribution.com',
    'html5.gamedistribution.com',
    'game-cdn.gamedistribution.com',
    'gd-hbcontent.htmlgames.com',
    'gamemonétize.com',
    
    # Scratch MIT域名
    'scratch.mit.edu',
    'cdn2.scratch.mit.edu',
    'uploads.scratch.mit.edu',
    'projects.scratch.mit.edu',
    
    # Miniplay域名
    'miniplay.com',
    'static.miniplay.com',
    'games.miniplay.com',
    'cdn.miniplay.com',
    
    # 其他知名游戏平台
    'poki.com/embed',
    'embed.poki.com',
    'kongregate.com/games',
    'armor.ag/onstage',
    'www.kongregate.com/games',
    
    # HTML5游戏CDN
    'html5.gamedistribution.com',
    'game-cdn.poki.com',
    'assets.crazygames.com',
    
    # 通用游戏托管
    'cloudfront.net',
    'amazonaws.com',
    'github.io',
    'netlify.app',
    'vercel.app'
]

# API搜索查询词（针对在线可玩游戏优化，包含新网站）
GAME_SEARCH_QUERIES = [
    # 针对特定平台的iframe游戏
    'site:itch.io "play in browser" iframe -forum -discussion -devlog',
    'site:gamejolt.com "play now" HTML5 -community -forum',
    'site:newgrounds.com "play online" -forum -review',
    'site:crazygames.com "play online" HTML5 -blog',
    'site:gamedistribution.com games HTML5 embed',
    'site:scratch.mit.edu projects "see inside" -tutorial',
    'site:miniplay.com games "play online" -news',
    'site:poki.com games "play online" -blog -news',
    
    # 通用在线游戏搜索（排除非游戏内容）
    '"play now" "in browser" HTML5 -download -forum -wiki -review -blog',
    '"browser game" iframe embed "play online" -tutorial -guide',
    'HTML5 games "no download" embed -forum -discussion -blog',
    '"web game" iframe "play instantly" -review -news -forum',
    '"online game" HTML5 canvas "play free" -download -app store'
]

# ========================================================================================
# 🎨 缩略图生成功能 - 集成到GameManager中
# ========================================================================================

class ThumbnailGenerator:
    """缩略图生成器"""
    
    def __init__(self, thumbnails_dir):
        self.thumbnails_dir = thumbnails_dir
        os.makedirs(thumbnails_dir, exist_ok=True)
    
    def generate_gradient_background(self, width, height, color1, color2):
        """生成渐变背景"""
        if not PIL_AVAILABLE:
            return None
            
        image = Image.new('RGB', (width, height))
        
        for y in range(height):
            # 计算渐变比例
            ratio = y / height
            
            # 线性插值
            r = int(color1[0] * (1 - ratio) + color2[0] * ratio)
            g = int(color1[1] * (1 - ratio) + color2[1] * ratio)
            b = int(color1[2] * (1 - ratio) + color2[2] * ratio)
            
            # 填充这一行
            for x in range(width):
                image.putpixel((x, y), (r, g, b))
        
        return image
    
    def generate_geometric_pattern(self, width, height, base_color):
        """生成几何图案背景"""
        if not PIL_AVAILABLE:
            return None
            
        image = Image.new('RGB', (width, height), base_color)
        draw = ImageDraw.Draw(image)
        
        # 随机几何图案
        patterns = ['circles', 'triangles', 'rectangles', 'lines']
        pattern = random.choice(patterns)
        
        # 生成亮色和暗色变体
        r, g, b = base_color
        light_color = (min(255, r + 40), min(255, g + 40), min(255, b + 40))
        dark_color = (max(0, r - 40), max(0, g - 40), max(0, b - 40))
        
        if pattern == 'circles':
            for _ in range(8):
                x = random.randint(0, width)
                y = random.randint(0, height)
                radius = random.randint(20, 60)
                color = random.choice([light_color, dark_color])
                draw.ellipse([x-radius, y-radius, x+radius, y+radius], 
                            fill=color, outline=None)
        
        elif pattern == 'triangles':
            for _ in range(6):
                points = []
                for _ in range(3):
                    points.append((random.randint(0, width), random.randint(0, height)))
                color = random.choice([light_color, dark_color])
                draw.polygon(points, fill=color)
        
        elif pattern == 'rectangles':
            for _ in range(10):
                x1 = random.randint(0, width//2)
                y1 = random.randint(0, height//2)
                x2 = x1 + random.randint(30, 80)
                y2 = y1 + random.randint(20, 60)
                color = random.choice([light_color, dark_color])
                draw.rectangle([x1, y1, x2, y2], fill=color)
        
        elif pattern == 'lines':
            for _ in range(15):
                x1 = random.randint(0, width)
                y1 = random.randint(0, height)
                x2 = random.randint(0, width)
                y2 = random.randint(0, height)
                color = random.choice([light_color, dark_color])
                draw.line([x1, y1, x2, y2], fill=color, width=random.randint(2, 8))
        
        return image
    
    def create_game_thumbnail(self, title, style='gradient', width=300, height=200):
        """创建游戏缩略图"""
        if not PIL_AVAILABLE:
            logger.warning("PIL不可用，无法生成缩略图")
            return None
            
        # 预定义的颜色主题
        color_themes = [
            {'primary': (52, 152, 219), 'secondary': (155, 89, 182)},
            {'primary': (46, 204, 113), 'secondary': (52, 152, 219)},
            {'primary': (230, 126, 34), 'secondary': (231, 76, 60)},
            {'primary': (155, 89, 182), 'secondary': (52, 73, 94)},
            {'primary': (231, 76, 60), 'secondary': (192, 57, 43)},
            {'primary': (26, 188, 156), 'secondary': (22, 160, 133)},
            {'primary': (241, 196, 15), 'secondary': (230, 126, 34)},
            {'primary': (52, 73, 94), 'secondary': (44, 62, 80)},
        ]
        
        theme = random.choice(color_themes)
        
        if style == 'gradient':
            image = self.generate_gradient_background(width, height, theme['primary'], theme['secondary'])
        else:
            image = self.generate_geometric_pattern(width, height, theme['primary'])
        
        if not image:
            return None
            
        draw = ImageDraw.Draw(image)
        
        # 尝试加载字体
        try:
            # Windows系统字体
            font_large = ImageFont.truetype("arial.ttf", 24)
        except:
            try:
                # Linux系统字体
                font_large = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 24)
            except:
                # 默认字体
                font_large = ImageFont.load_default()
        
        # 添加半透明覆盖层
        overlay = Image.new('RGBA', (width, height), (0, 0, 0, 80))
        image = Image.alpha_composite(image.convert('RGBA'), overlay).convert('RGB')
        draw = ImageDraw.Draw(image)
        
        # 处理标题文字
        if len(title) > 20:
            title = title[:17] + "..."
        
        # 获取文字颜色
        text_color = (255, 255, 255)  # 白色文字在深色覆盖层上
        
        # 计算文字位置（居中）
        bbox = draw.textbbox((0, 0), title, font=font_large)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        
        text_x = (width - text_width) // 2
        text_y = (height - text_height) // 2
        
        # 添加文字阴影
        shadow_offset = 2
        draw.text((text_x + shadow_offset, text_y + shadow_offset), title, 
                 fill=(0, 0, 0), font=font_large)
        
        # 添加主文字
        draw.text((text_x, text_y), title, fill=text_color, font=font_large)
        
        # 添加装饰元素
        if random.choice([True, False]):
            # 添加小图标或装饰
            icon_size = 20
            icon_x = width - icon_size - 10
            icon_y = 10
            
            # 简单的游戏手柄图标
            draw.ellipse([icon_x, icon_y, icon_x + icon_size, icon_y + icon_size], 
                        fill=text_color, outline=None)
            draw.ellipse([icon_x + 4, icon_y + 4, icon_x + icon_size - 4, icon_y + icon_size - 4], 
                        fill=theme['primary'], outline=None)
        
        return image
    
    def save_thumbnail(self, image, filename):
        """保存缩略图"""
        if not image:
            return False
            
        filepath = os.path.join(self.thumbnails_dir, filename)
        try:
            image.save(filepath, 'JPEG', quality=90, optimize=True)
            return True
        except Exception as e:
            logger.error(f"保存缩略图失败 {filename}: {e}")
            return False
    
    def generate_for_game(self, game_title, game_id):
        """为特定游戏生成缩略图"""
        style = random.choice(['gradient', 'geometric'])
        image = self.create_game_thumbnail(game_title, style)
        
        if image:
            filename = f"{game_id}.jpg"
            if self.save_thumbnail(image, filename):
                return f'/games/thumbnails/{filename}'
        
        return '/games/thumbnails/default.jpg'

class GameManager:
    """统一的游戏管理器"""
    
    def __init__(self):
        self.session = requests.Session()
        
        # 确保目录存在
        os.makedirs(LOCAL_GAMES_DIR, exist_ok=True)
        os.makedirs(THUMBNAILS_DIR, exist_ok=True)
        
        # 检查API配置
        self.has_serpapi = bool(SERPAPI_KEY)
        self.has_google_api = bool(GOOGLE_API_KEY and GOOGLE_CX)
        
        if self.has_serpapi:
            logger.info("✅ SerpAPI 已配置")
        if self.has_google_api:
            logger.info("✅ Google Custom Search API 已配置")
        if not (self.has_serpapi or self.has_google_api):
            logger.info("⚠️ 未配置API密钥，将使用基础爬虫功能")
        
        # 显示代理状态
        if USE_PROXY:
            if PROXY_AVAILABLE:
                logger.info(f"✅ 全局代理已启用: {PROXY_HOST}:{PROXY_PORT}")
                logger.info("  - 环境变量已设置，所有HTTP请求将走代理")
            else:
                logger.info("⚠️ 代理配置失败，将直接连接")
        else:
            logger.info("ℹ️ 代理模式未启用，直接连接网络")
        
        # 显示反爬虫策略状态
        logger.info("🛡️ 反爬虫策略已启用:")
        logger.info("  - 智能延迟（GameJolt: 3-6s, itch.io: 2-4s）")
        logger.info("  - 特殊请求头（模拟真实浏览器）")
        logger.info("  - URL模式推断（应对403错误）")
        
        # 显示白名单模式状态
        if STRICT_WHITELIST:
            logger.info("🔒 严格白名单模式：只接受预定义的可信域名")
        else:
            logger.info("🤖 智能验证模式：白名单优先 + AI评分系统")
            logger.info(f"  - 白名单域名: {len(EMBEDDABLE_DOMAINS)} 个")
            logger.info("  - 智能评分: 基于域名、路径、文件名等特征")
        
        # 初始化请求延迟跟踪
        self.last_request_time = {}
        self.domain_request_count = {}
        
        # 跟踪429错误的域名（用于增加延迟）
        self.rate_limited_domains = set()
        
        # 初始化缩略图生成器
        if PIL_AVAILABLE:
            self.thumbnail_generator = ThumbnailGenerator(THUMBNAILS_DIR)
            logger.info("✅ 缩略图生成器已启用")
        else:
            self.thumbnail_generator = None
            logger.info("⚠️ PIL库未安装，缩略图生成功能不可用")
    
    @retry(stop=stop_after_attempt(3), 
           wait=wait_fixed(2),
           retry=retry_if_exception_type((RequestException, ConnectionError, Timeout)))
    def _make_request(self, url, method='get', **kwargs):
        """带重试机制的HTTP请求（使用全局代理）"""
        headers = kwargs.pop('headers', get_random_headers())
        
        # 智能延迟策略
        self._apply_smart_delay(url)
        
        # 全局代理已通过环境变量设置，无需手动指定
        # requests会自动使用HTTP_PROXY/HTTPS_PROXY环境变量
        
        try:
            if method.lower() == 'head':
                response = self.session.head(url, headers=headers, timeout=10, **kwargs)
            else:
                response = self.session.get(url, headers=headers, timeout=15, **kwargs)
            response.raise_for_status()
            return response
        except requests.exceptions.HTTPError as e:
            # 特殊处理429错误（频率限制）
            if hasattr(e.response, 'status_code') and e.response.status_code == 429:
                domain = urlparse(url).netloc
                self.rate_limited_domains.add(domain)
                logger.error(f"🚫 429错误！{domain} 请求过于频繁，已标记为高风险域名")
                # 立即等待一段时间
                logger.info("⏳ 立即休息30秒以避免继续触发限制...")
                time.sleep(30)
            # 特殊处理403错误（内容保护）
            elif hasattr(e.response, 'status_code') and e.response.status_code == 403:
                domain = urlparse(url).netloc
                logger.debug(f"🛡️ {domain} 403错误（内容保护），尝试使用推断URL")
            logger.warning(f"请求失败 {url}: {e}")
            raise
        except Exception as e:
            logger.warning(f"请求失败 {url}: {e}")
            raise
    
    def _apply_smart_delay(self, url: str):
        """智能延迟策略，根据域名和请求频率调整"""
        parsed = urlparse(url)
        domain = parsed.netloc
        current_time = time.time()
        
        # 跟踪每个域名的请求次数
        if domain not in self.domain_request_count:
            self.domain_request_count[domain] = 0
        self.domain_request_count[domain] += 1
        
        # 根据域名使用配置文件中的延迟策略
        platform = 'default'
        for platform_name in Config.PLATFORM_DELAYS.keys():
            if platform_name != 'default' and platform_name in domain:
                platform = platform_name
                break
        
        min_delay, max_delay = Config.PLATFORM_DELAYS[platform]
        logger.debug(f"🚦 [{platform}] 使用延迟: {min_delay}-{max_delay}s")
        
        # 如果请求过于频繁，增加延迟
        request_count = self.domain_request_count[domain]
        if request_count > 5:
            min_delay *= 1.5
            max_delay *= 1.5
            logger.warning(f"⚠️ [{domain}] 请求频繁，延迟增加到 {min_delay:.1f}-{max_delay:.1f}s")
        
        # 检查是否有429错误历史，如果有则大幅增加延迟
        if hasattr(self, 'rate_limited_domains') and domain in self.rate_limited_domains:
            min_delay *= 2.0
            max_delay *= 2.0
            logger.warning(f"🚫 [{domain}] 检测到429错误历史，延迟增加到 {min_delay:.1f}-{max_delay:.1f}s")
        
        # 确保与上次请求的时间间隔
        if domain in self.last_request_time:
            elapsed = current_time - self.last_request_time[domain]
            if elapsed < min_delay:
                sleep_time = min_delay - elapsed + random.uniform(0, 1)
                time.sleep(sleep_time)
        
        # 记录请求时间
        self.last_request_time[domain] = time.time()
        
        # 基础随机延迟
        time.sleep(random.uniform(min_delay, max_delay))
    
    def read_games_file(self) -> List[Dict]:
        """读取当前games.ts文件中的游戏数据"""
        try:
            with open(GAMES_DATA_FILE, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 提取games数组
            start_marker = 'export const games: Game[] = ['
            end_marker = '];'
            
            start_idx = content.find(start_marker)
            if start_idx == -1:
                logger.error("找不到games数组开始标记")
                return []
            
            start_idx += len(start_marker)
            end_idx = content.find(end_marker, start_idx)
            if end_idx == -1:
                logger.error("找不到games数组结束标记")
                return []
            
            games_str = content[start_idx:end_idx].strip()
            
            # 简单解析游戏对象
            games = []
            game_objects = self._extract_game_objects(games_str)
            
            for game_obj in game_objects:
                game_data = self._parse_game_object(game_obj)
                if game_data:
                    games.append(game_data)
            
            logger.info(f"成功读取 {len(games)} 个游戏")
            return games
            
        except Exception as e:
            logger.error(f"读取games.ts文件失败: {e}")
            return []
    
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
                'description': r"description:\s*['\"]([^'\"]+)['\"]",
                'category': r"category:\s*['\"]([^'\"]+)['\"]",
                'categoryId': r"categoryId:\s*['\"]([^'\"]+)['\"]",
                'thumbnail': r"thumbnail:\s*['\"]([^'\"]+)['\"]",
                'path': r"path:\s*['\"]([^'\"]+)['\"]",
                'featured': r"featured:\s*(true|false)",
                'type': r"type:\s*['\"]([^'\"]+)['\"]",
                'iframeUrl': r"iframeUrl:\s*['\"]([^'\"]+)['\"]",
                'staticPath': r"staticPath:\s*['\"]([^'\"]+)['\"]",
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
            
            # 提取tags数组
            tags_match = re.search(r'tags:\s*\[(.*?)\]', obj_str, re.DOTALL)
            if tags_match:
                tags_str = tags_match.group(1)
                tags = [tag.strip(' "\'') for tag in tags_str.split(',') if tag.strip(' "\'')]
                game['tags'] = tags
            
            return game if 'id' in game and 'title' in game else None
            
        except Exception as e:
            logger.warning(f"解析游戏对象失败: {e}")
            return None
    
    def clean_games(self) -> List[Dict]:
        """清理游戏数据，移除无效游戏"""
        games = self.read_games_file()
        valid_games = []
        
        for game in games:
            # 检查必需字段
            if not all(key in game for key in ['id', 'title', 'type']):
                logger.warning(f"游戏缺少必需字段: {game.get('title', 'Unknown')}")
                continue
            
            # 检查标题有效性
            title = game['title'].strip()
            if len(title) < 2 or len(title) > 100:
                logger.warning(f"游戏标题无效: {title}")
                continue
            
            # 检查类型和URL
            if game['type'] == 'iframe':
                if 'iframeUrl' not in game:
                    logger.warning(f"iframe游戏缺少URL: {title}")
                    continue
                
                # 检查是否是可嵌入的域名
                parsed = urlparse(game['iframeUrl'])
                if not any(domain in parsed.netloc for domain in EMBEDDABLE_DOMAINS):
                    logger.warning(f"域名不在白名单中: {parsed.netloc} - {title}")
                    continue
            
            elif game['type'] == 'static':
                if 'staticPath' not in game:
                    logger.warning(f"静态游戏缺少路径: {title}")
                    continue
            
            valid_games.append(game)
        
        logger.info(f"清理完成: {len(valid_games)}/{len(games)} 个有效游戏")
        return valid_games
    
    def remove_duplicates(self, games: List[Dict]) -> List[Dict]:
        """移除重复游戏"""
        seen_titles = set()
        seen_urls = set()
        unique_games = []
        
        for game in games:
            title = game['title'].lower().strip()
            
            # 检查标题重复
            if title in seen_titles:
                logger.info(f"移除重复标题: {game['title']}")
                continue
            
            # 检查URL重复
            url_key = game.get('iframeUrl') or game.get('staticPath', '')
            if url_key and url_key in seen_urls:
                logger.info(f"移除重复URL: {game['title']}")
                continue
            
            seen_titles.add(title)
            if url_key:
                seen_urls.add(url_key)
            
            unique_games.append(game)
        
        logger.info(f"去重完成: {len(unique_games)}/{len(games)} 个唯一游戏")
        return unique_games
    
    def fix_thumbnails(self, games: List[Dict]) -> List[Dict]:
        """修复游戏封面，自动生成或分配合适的缩略图"""
        try:
            # 获取可用的缩略图文件
            available_thumbs = []
            for file in os.listdir(THUMBNAILS_DIR):
                if file.lower().endswith(('.jpg', '.jpeg', '.png', '.gif')):
                    available_thumbs.append(file)
            
            # 排除default.jpg
            available_thumbs = [thumb for thumb in available_thumbs if thumb != 'default.jpg']
            available_thumbs.sort()  # 按文件名排序
            
            logger.info(f"找到 {len(available_thumbs)} 个现有缩略图")
            
            # 为每个游戏分配或生成缩略图
            for i, game in enumerate(games):
                game_id = game.get('id', f'game_{i}')
                game_title = game.get('title', 'Untitled Game')
                
                # 检查是否已有专属缩略图
                specific_thumb = f"{game_id}.jpg"
                specific_thumb_path = os.path.join(THUMBNAILS_DIR, specific_thumb)
                
                if os.path.exists(specific_thumb_path):
                    # 使用现有的专属缩略图
                    game['thumbnail'] = f'/games/thumbnails/{specific_thumb}'
                    logger.debug(f"使用现有缩略图: {game_title} -> {specific_thumb}")
                
                elif PIL_AVAILABLE and self.thumbnail_generator:
                    # 自动生成新缩略图
                    logger.info(f"🎨 为游戏 '{game_title}' 生成新缩略图...")
                    generated_thumb = self.thumbnail_generator.generate_for_game(game_title, game_id)
                    game['thumbnail'] = generated_thumb
                    logger.info(f"✅ 生成完成: {game_title}")
                
                elif available_thumbs:
                    # 循环使用可用的缩略图
                    thumb_index = i % len(available_thumbs)
                    thumbnail_file = available_thumbs[thumb_index]
                    game['thumbnail'] = f'/games/thumbnails/{thumbnail_file}'
                    logger.info(f"分配现有缩略图: {game_title} -> {thumbnail_file}")
                
                else:
                    # 使用默认缩略图
                    game['thumbnail'] = '/games/thumbnails/default.jpg'
                    logger.warning(f"使用默认缩略图: {game_title}")
            
            return games
            
        except Exception as e:
            logger.error(f"修复缩略图失败: {e}")
            return games
    
    def write_games_file(self, games: List[Dict]):
        """写入游戏数据到games.ts文件"""
        try:
            # 备份原文件
            backup_file = f"{GAMES_DATA_FILE}.backup.{int(time.time())}"
            shutil.copy2(GAMES_DATA_FILE, backup_file)
            logger.info(f"已备份原文件: {backup_file}")
            
            # 读取原文件内容
            with open(GAMES_DATA_FILE, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 更新分类计数
            category_counts = {}
            for game in games:
                cat_id = game.get('categoryId', '1')
                category_counts[cat_id] = category_counts.get(cat_id, 0) + 1
            
            # 更新categories部分
            categories_pattern = r'export const categories: Category\[\] = \[(.*?)\];'
            categories_match = re.search(categories_pattern, content, re.DOTALL)
            
            if categories_match:
                categories_content = categories_match.group(1)
                
                # 更新每个分类的count
                def update_count(match):
                    cat_data = match.group(0)
                    id_match = re.search(r"id:\s*['\"](\d+)['\"]", cat_data)
                    if id_match:
                        cat_id = id_match.group(1)
                        count = category_counts.get(cat_id, 0)
                        return re.sub(r'count:\s*\d+', f'count: {count}', cat_data)
                    return cat_data
                
                updated_categories = re.sub(r'\{[^}]+\}', update_count, categories_content)
                content = content.replace(categories_match.group(1), updated_categories)
            
            # 生成游戏数组代码
            games_code = self._generate_games_code(games)
            
            # 替换games数组
            start_marker = 'export const games: Game[] = ['
            end_marker = '];'
            
            start_idx = content.find(start_marker)
            end_idx = content.find(end_marker, start_idx) + len(end_marker)
            
            if start_idx != -1 and end_idx != -1:
                new_content = (
                    content[:start_idx] + 
                    start_marker + '\n' + 
                    games_code + '\n' + 
                    end_marker + 
                    content[end_idx:]
                )
                
                # 写入文件
                with open(GAMES_DATA_FILE, 'w', encoding='utf-8') as f:
                    f.write(new_content)
                
                logger.info(f"✅ 成功更新games.ts文件，包含 {len(games)} 个游戏")
            else:
                logger.error("无法找到games数组位置")
                
        except Exception as e:
            logger.error(f"写入games.ts文件失败: {e}")
    
    def _generate_games_code(self, games: List[Dict]) -> str:
        """生成游戏数组的TypeScript代码"""
        lines = []
        
        for game in games:
            lines.append('  {')
            lines.append(f"    id: '{game['id']}',")
            lines.append(f"    title: '{game['title']}',")
            lines.append(f"    description: '{game.get('description', '')}',")
            lines.append(f"    category: '{game.get('category', '休闲')}',")
            lines.append(f"    categoryId: '{game.get('categoryId', '1')}',")
            lines.append(f"    thumbnail: '{game.get('thumbnail', '/games/thumbnails/default.jpg')}',")
            lines.append(f"    path: '{game.get('path', f'/games/{game['id']}')}',")
            lines.append(f"    featured: {str(game.get('featured', False)).lower()},")
            lines.append(f"    type: '{game['type']}',")
            
            if game['type'] == 'iframe':
                lines.append(f"    iframeUrl: '{game['iframeUrl']}',")
            elif game['type'] == 'static':
                lines.append(f"    staticPath: '{game['staticPath']}',")
            
            lines.append(f"    addedAt: '{game.get('addedAt', datetime.now().strftime('%Y-%m-%d'))}',")
            
            tags = game.get('tags', ['休闲'])
            tags_str = ', '.join([f'"{tag}"' for tag in tags])
            lines.append(f"    tags: [{tags_str}]")
            lines.append('  },')
        
        return '\n'.join(lines)
    
    def crawl_new_games(self, max_games: int = 10) -> List[Dict]:
        """爬取新游戏（组合使用基础爬虫和API搜索）"""
        logger.info("🚀 开始爬取新游戏...")
        all_new_games = []
        
        # 1. 基础爬虫（多个平台）
        basic_games = self._crawl_basic_sites(max_games // 2)
        all_new_games.extend(basic_games)
        
        # 2. API搜索（如果配置了API）
        if self.has_serpapi or self.has_google_api:
            api_games = self._crawl_with_api(max_games - len(all_new_games))
            all_new_games.extend(api_games)
        
        logger.info(f"爬取完成，总共找到 {len(all_new_games)} 个新游戏")
        return all_new_games
    
    def _crawl_basic_sites(self, max_games: int) -> List[Dict]:
        """基础站点爬虫（支持多个平台，智能检测选择器）"""
        logger.info("🌐 开始基础站点爬取...")
        new_games = []
        
        for site in PREMIUM_GAME_SITES:
            if len(new_games) >= max_games:
                break
                
            try:
                logger.info(f"爬取平台: {site['name']}")
                response = self._make_request(site['search_url'])
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # 智能检测选择器（如果未配置的话）
                game_selector = site.get('game_selector')
                title_selector = site.get('title_selector')
                
                if not game_selector or not title_selector:
                    logger.info(f"🔍 自动检测 {site['name']} 的CSS选择器...")
                    detected_selectors = self._detect_game_selectors(soup, site['name'])
                    
                    if not game_selector:
                        game_selector = detected_selectors.get('game_selector')
                    if not title_selector:
                        title_selector = detected_selectors.get('title_selector')
                    
                    if game_selector and title_selector:
                        logger.info(f"✅ 检测成功: game='{game_selector}', title='{title_selector}'")
                    else:
                        logger.warning(f"❌ 选择器检测失败，跳过平台: {site['name']}")
                        continue
                
                game_elements = soup.select(game_selector)[:max_games - len(new_games)]
                logger.info(f"找到 {len(game_elements)} 个游戏元素")
                
                for i, element in enumerate(game_elements):
                    try:
                        title_elem = element.select_one(title_selector)
                        if not title_elem:
                            # 尝试备用标题选择器
                            title_elem = self._find_title_element(element)
                        
                        if not title_elem:
                            continue
                        
                        title = title_elem.get_text(strip=True)
                        if len(title) < 3:
                            continue
                        
                        link_elem = element.select_one('a[href]')
                        if not link_elem:
                            # 如果元素本身就是链接
                            if element.name == 'a' and element.get('href'):
                                link_elem = element
                            else:
                                continue
                        
                        game_url = urljoin(site['base_url'], link_elem['href'])
                        
                        # 尝试查找iframe URL
                        iframe_url = self._find_iframe_url(game_url)
                        if iframe_url and self._verify_iframe_playable(iframe_url):
                            game_id = f"basic_{site['name'].lower().replace(' ', '_')}_{int(time.time())}_{i}"
                            
                            game_info = {
                                'id': game_id,
                                'title': title,
                                'description': f"来自{site['name']}的HTML5游戏",
                                'category': '休闲',
                                'categoryId': '1',
                                'thumbnail': '/games/thumbnails/default.jpg',
                                'path': f'/games/{game_id}',
                                'featured': False,
                                'type': 'iframe',
                                'iframeUrl': iframe_url,
                                'addedAt': datetime.now().strftime('%Y-%m-%d'),
                                'tags': ['HTML5', '在线', site['name']]
                            }
                            new_games.append(game_info)
                            logger.info(f"✅ 基础爬取找到游戏: {title} - {site['name']}")
                        
                        time.sleep(random.uniform(2, 4))
                        
                    except Exception as e:
                        logger.error(f"处理游戏失败: {e}")
                        continue
                
            except Exception as e:
                logger.error(f"平台 {site['name']} 爬取失败: {e}")
                continue
        
        logger.info(f"基础爬取完成，找到 {len(new_games)} 个游戏")
        return new_games
    
    def _detect_game_selectors(self, soup: BeautifulSoup, site_name: str) -> Dict[str, str]:
        """智能检测游戏相关的CSS选择器"""
        # 常见的游戏容器选择器模式
        game_container_patterns = [
            # 常见的class名称模式
            '.game', '.game-item', '.game-card', '.game-cell', '.game-tile',
            '.game-thumbnail', '.game-box', '.game-entry', '.game-listing',
            '[class*="game"]', '[class*="item"]', '[class*="card"]', 
            '[class*="thumb"]', '[class*="entry"]',
            
            # ID模式
            '[id*="game"]', '[id*="item"]',
            
            # 通用容器
            '.item', '.card', '.entry', '.box', '.tile', '.cell',
            '.thumbnail', '.thumb', '.listing', '.product'
        ]
        
        # 常见的标题选择器模式
        title_patterns = [
            '.title', '.name', '.game-title', '.game-name', '.item-title',
            '.card-title', '.entry-title', '.product-title',
            'h1', 'h2', 'h3', 'h4', '.heading',
            '[class*="title"]', '[class*="name"]', '[class*="heading"]',
            'a', '.link'
        ]
        
        best_game_selector = None
        best_title_selector = None
        best_score = 0
        
        logger.debug(f"🔍 分析 {site_name} 页面结构...")
        
        # 测试游戏容器选择器
        for game_pattern in game_container_patterns:
            try:
                game_elements = soup.select(game_pattern)
                
                # 过滤掉明显不合理的结果
                if len(game_elements) < 3 or len(game_elements) > 100:
                    continue
                
                # 测试标题选择器
                for title_pattern in title_patterns:
                    score = self._evaluate_selector_combination(
                        game_elements, title_pattern, site_name)
                    
                    if score > best_score:
                        best_score = score
                        best_game_selector = game_pattern
                        best_title_selector = title_pattern
                        
            except Exception as e:
                logger.debug(f"选择器测试失败 {game_pattern}: {e}")
                continue
        
        result = {}
        if best_game_selector and best_title_selector and best_score > 5:
            result['game_selector'] = best_game_selector
            result['title_selector'] = best_title_selector
            logger.info(f"🎯 最佳选择器组合 (得分: {best_score})")
        else:
            logger.warning(f"⚠️ 未找到合适的选择器组合 (最高得分: {best_score})")
        
        return result
    
    def _evaluate_selector_combination(self, game_elements: list, title_pattern: str, site_name: str) -> int:
        """评估选择器组合的质量"""
        score = 0
        valid_titles = 0
        has_links = 0
        
        # 取样测试（最多测试前10个元素）
        sample_elements = game_elements[:min(10, len(game_elements))]
        
        for element in sample_elements:
            try:
                # 测试标题选择器
                title_elem = element.select_one(title_pattern)
                if title_elem:
                    title_text = title_elem.get_text(strip=True)
                    
                    # 验证标题质量
                    if self._is_valid_game_title(title_text):
                        valid_titles += 1
                        score += 2
                
                # 检查是否包含链接
                link_elem = element.select_one('a[href]')
                if link_elem or (element.name == 'a' and element.get('href')):
                    has_links += 1
                    score += 1
                
                # 检查元素结构合理性
                if self._has_reasonable_structure(element):
                    score += 1
                    
            except Exception:
                continue
        
        # 计算质量比例
        if len(sample_elements) > 0:
            title_ratio = valid_titles / len(sample_elements)
            link_ratio = has_links / len(sample_elements)
            
            # 标题覆盖率权重
            score += int(title_ratio * 10)
            # 链接覆盖率权重
            score += int(link_ratio * 5)
            
            # 数量合理性奖励
            total_elements = len(game_elements)
            if 5 <= total_elements <= 50:
                score += 5
            elif 3 <= total_elements <= 100:
                score += 3
        
        return score
    
    def _is_valid_game_title(self, title: str) -> bool:
        """验证是否是有效的游戏标题"""
        if not title or len(title.strip()) < 2:
            return False
        
        # 过滤掉明显不是游戏的标题
        invalid_keywords = [
            'menu', 'navigation', 'header', 'footer', 'sidebar',
            'advertisement', 'ad', 'sponsor', 'login', 'register',
            'search', 'filter', 'sort', 'category', 'tag',
            'more', 'view all', 'load more', 'next', 'previous',
            'home', 'about', 'contact', 'privacy', 'terms'
        ]
        
        title_lower = title.lower()
        if any(keyword in title_lower for keyword in invalid_keywords):
            return False
        
        # 检查长度合理性
        if len(title) > 100:
            return False
        
        # 包含游戏相关词汇加分
        game_keywords = ['game', 'play', 'adventure', 'puzzle', 'action', 'fun']
        if any(keyword in title_lower for keyword in game_keywords):
            return True
        
        # 基本验证：包含字母和合理长度
        return len(title.strip()) >= 3 and any(c.isalpha() for c in title)
    
    def _has_reasonable_structure(self, element) -> bool:
        """检查元素是否有合理的游戏条目结构"""
        # 检查是否包含基本的游戏信息元素
        has_image = bool(element.select('img'))
        has_link = bool(element.select('a[href]')) or (element.name == 'a' and element.get('href'))
        has_text_content = bool(element.get_text(strip=True))
        
        # 至少要有链接和文本内容
        return has_link and has_text_content
    
    def _find_title_element(self, element):
        """在元素中查找最可能的标题元素"""
        # 按优先级尝试不同的标题选择器
        title_selectors = [
            '.title', '.name', '.game-title', '.game-name',
            'h1', 'h2', 'h3', 'h4',
            '[class*="title"]', '[class*="name"]',
            'a[href]'  # 链接文本通常是标题
        ]
        
        for selector in title_selectors:
            title_elem = element.select_one(selector)
            if title_elem:
                title_text = title_elem.get_text(strip=True)
                if self._is_valid_game_title(title_text):
                    return title_elem
        
        return None
    
    def _crawl_with_api(self, max_games: int) -> List[Dict]:
        """使用API搜索游戏（优化版）"""
        logger.info("🔍 开始API搜索...")
        api_games = []
        
        for query in GAME_SEARCH_QUERIES[:3]:  # 限制查询数量
            if len(api_games) >= max_games:
                break
                
            logger.info(f"搜索查询: {query}")
            
            # 优先使用SerpAPI
            if self.has_serpapi:
                serp_results = self._search_with_serpapi_enhanced(query, max_games - len(api_games))
                api_games.extend(serp_results)
                time.sleep(random.uniform(3, 5))  # 避免请求过快
            
            # 备用Google Custom Search
            elif self.has_google_api:
                google_results = self._search_with_google(query, max_games - len(api_games))
                api_games.extend(google_results)
                time.sleep(random.uniform(3, 5))
        
        logger.info(f"API搜索完成，找到 {len(api_games)} 个游戏")
        return api_games
    
    @retry(stop=stop_after_attempt(3), wait=wait_fixed(3))
    def _search_with_serpapi_enhanced(self, query: str, max_results: int) -> List[Dict]:
        """使用SerpAPI搜索（增强版）"""
        results = []
        
        try:
            if SERPAPI_AVAILABLE:
                # 使用正确的SerpAPI调用方式
                params = {
                    'q': query,
                    'api_key': SERPAPI_KEY,
                    'engine': 'google',
                    'num': min(max_results, 10),
                    'hl': 'en',
                    'gl': 'us'
                }
                
                # 使用正确的search方法，传入字典参数
                search_results = serpapi.search(params)
                # SerpResults对象需要转换为字典
                data = search_results.as_dict() if hasattr(search_results, 'as_dict') else search_results
            
            else:
                # 备用HTTP调用
                params = {
                    'q': query,
                    'api_key': SERPAPI_KEY,
                    'engine': 'google',
                    'num': min(max_results, 10),
                    'hl': 'en'
                }
                
                response = self._make_request('https://serpapi.com/search', params=params)
                data = response.json()
            
            for i, result in enumerate(data.get('organic_results', [])[:max_results]):
                try:
                    title = result.get('title', '').strip()
                    link = result.get('link', '')
                    snippet = result.get('snippet', '')
                    
                    if not title or not link or len(title) < 3:
                        continue
                    
                    # 验证是否是游戏相关
                    if not self._is_game_related(title, snippet):
                        logger.debug(f"❌ SerpAPI跳过非游戏内容: {title}")
                        continue
                    
                    # 尝试查找iframe URL
                    iframe_url = self._find_iframe_url(link)
                    if not iframe_url:
                        logger.debug(f"❌ SerpAPI未找到iframe: {title}")
                        continue
                    
                    if not self._verify_iframe_playable(iframe_url):
                        logger.debug(f"❌ SerpAPI iframe不可用: {title}")
                        continue
                    
                    game_id = f"serp_{int(time.time())}_{i}"
                    
                    game_info = {
                        'id': game_id,
                        'title': self._clean_title(title),
                        'description': f"通过SerpAPI发现的HTML5游戏: {snippet[:100]}...",
                        'category': self._categorize_game(title, snippet),
                        'categoryId': self._get_category_id(title, snippet),
                        'thumbnail': '/games/thumbnails/default.jpg',
                        'path': f'/games/{game_id}',
                        'featured': False,
                        'type': 'iframe',
                        'iframeUrl': iframe_url,
                        'addedAt': datetime.now().strftime('%Y-%m-%d'),
                        'tags': ['API搜索', 'HTML5', 'SerpAPI']
                    }
                    results.append(game_info)
                    logger.info(f"✅ SerpAPI找到游戏: {title}")
                
                except Exception as e:
                    logger.warning(f"处理SerpAPI结果失败: {e}")
                    continue
        
        except Exception as e:
            logger.error(f"SerpAPI搜索失败: {e}")
            raise
        
        return results
    
    @retry(stop=stop_after_attempt(3), wait=wait_fixed(3))
    def _search_with_google(self, query: str, max_results: int) -> List[Dict]:
        """使用Google Custom Search API搜索"""
        results = []
        
        try:
            params = {
                'key': GOOGLE_API_KEY,
                'cx': GOOGLE_CX,
                'q': query,
                'num': min(max_results, 10)
            }
            
            response = self._make_request('https://www.googleapis.com/customsearch/v1', params=params)
            data = response.json()
            
            for i, item in enumerate(data.get('items', [])[:max_results]):
                try:
                    title = item.get('title', '').strip()
                    link = item.get('link', '')
                    snippet = item.get('snippet', '')
                    
                    if not title or not link or len(title) < 3:
                        continue
                    
                    # 验证是否是游戏相关
                    if not self._is_game_related(title, snippet):
                        continue
                    
                    # 尝试查找iframe URL
                    iframe_url = self._find_iframe_url(link)
                    if iframe_url and self._verify_iframe_playable(iframe_url):
                        game_id = f"google_{int(time.time())}_{i}"
                        
                        game_info = {
                            'id': game_id,
                            'title': self._clean_title(title),
                            'description': f"通过Google Custom Search发现的HTML5游戏: {snippet[:100]}...",
                            'category': self._categorize_game(title, snippet),
                            'categoryId': self._get_category_id(title, snippet),
                            'thumbnail': '/games/thumbnails/default.jpg',
                            'path': f'/games/{game_id}',
                            'featured': False,
                            'type': 'iframe',
                            'iframeUrl': iframe_url,
                            'addedAt': datetime.now().strftime('%Y-%m-%d'),
                            'tags': ['API搜索', 'HTML5', 'Google']
                        }
                        results.append(game_info)
                        logger.info(f"✅ Google API找到游戏: {title}")
                
                except Exception as e:
                    logger.warning(f"处理Google API结果失败: {e}")
                    continue
        
        except Exception as e:
            logger.error(f"Google Custom Search失败: {e}")
            raise
        
        return results
    
    def _is_game_related(self, title: str, snippet: str) -> bool:
        """验证标题和摘要是否与游戏相关且可在线玩"""
        text = (title + ' ' + snippet).lower()
        
        # 必须包含的游戏关键词
        game_keywords = [
            'game', 'play', 'html5', 'browser', 'online',
            'arcade', 'puzzle', 'action', 'adventure', 'strategy', 'casual',
            '游戏', '玩', '在线'
        ]
        
        # 可在线玩的关键词
        playable_keywords = [
            'play now', 'play online', 'in browser', 'play free',
            'no download', 'instant play', 'web game', 'browser game',
            'click to play', 'start playing', 'play instantly'
        ]
        
        # 排除的关键词（论坛、下载、新闻等）
        exclude_keywords = [
            'forum', 'discussion', 'review', 'news', 'blog', 'tutorial',
            'guide', 'download', 'wiki', 'community', 'devlog', 'discord',
            'reddit', 'youtube', 'steam', 'app store', 'google play',
            'walkthrough', 'cheats', 'tips', 'trailer', 'preview'
        ]
        
        # 必须包含游戏关键词
        has_game_keyword = any(keyword in text for keyword in game_keywords)
        
        # 最好包含可玩关键词
        has_playable_keyword = any(keyword in text for keyword in playable_keywords)
        
        # 不能包含排除关键词
        has_exclude_keyword = any(keyword in text for keyword in exclude_keywords)
        
        # 判断逻辑：有游戏关键词，没有排除关键词，最好有可玩关键词
        return has_game_keyword and not has_exclude_keyword and (has_playable_keyword or 'itch.io' in text or 'gamejolt' in text)
    
    def _clean_title(self, title: str) -> str:
        """清理游戏标题"""
        # 移除常见的后缀
        suffixes = [' - Play Online', ' | Free Game', ' - Browser Game', ' Online']
        for suffix in suffixes:
            if title.endswith(suffix):
                title = title[:-len(suffix)]
        
        return title.strip()
    
    def _categorize_game(self, title: str, snippet: str) -> str:
        """根据标题和摘要自动分类游戏"""
        text = (title + ' ' + snippet).lower()
        
        if any(word in text for word in ['puzzle', 'brain', 'logic', 'match', '益智', '谜题']):
            return '益智'
        elif any(word in text for word in ['action', 'shoot', 'fight', 'run', '动作', '射击']):
            return '动作'
        elif any(word in text for word in ['card', 'poker', 'solitaire', '卡牌', '纸牌']):
            return '卡牌'
        elif any(word in text for word in ['sport', 'football', 'soccer', 'basketball', '体育', '足球']):
            return '体育'
        elif any(word in text for word in ['board', 'chess', 'checkers', '棋盘', '象棋']):
            return '棋盘'
        else:
            return '休闲'
    
    def _get_category_id(self, title: str, snippet: str) -> str:
        """获取分类ID"""
        category = self._categorize_game(title, snippet)
        category_map = {
            '休闲': '1',
            '益智': '2',
            '动作': '3',
            '卡牌': '4',
            '体育': '5',
            '棋盘': '6'
        }
        return category_map.get(category, '1')
    
    @retry(stop=stop_after_attempt(2), wait=wait_fixed(3))
    def _find_iframe_url(self, game_url: str) -> Optional[str]:
        """在游戏页面中查找iframe URL（增强版）"""
        try:
            # 对于某些平台使用特殊的请求头
            special_headers = self._get_special_headers(game_url)
            response = self._make_request(game_url, headers=special_headers)
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # 1. 优先查找明确的游戏iframe
            game_iframes = soup.select('iframe[src*="game"], iframe[class*="game"], iframe[id*="game"]')
            for iframe in game_iframes:
                iframe_src = iframe.get('src')
                if iframe_src and self._is_valid_game_iframe(iframe_src, game_url):
                    return urljoin(game_url, iframe_src)
            
            # 2. 查找所有iframe，按可信度排序
            all_iframes = soup.select('iframe[src]')
            valid_iframes = []
            
            for iframe in all_iframes:
                iframe_src = iframe.get('src')
                if iframe_src:
                    full_url = urljoin(game_url, iframe_src)
                    if self._is_valid_game_iframe(iframe_src, game_url):
                        # 计算可信度分数
                        score = self._calculate_iframe_score(iframe, full_url)
                        valid_iframes.append((full_url, score))
            
            # 按分数排序，返回最高分的
            if valid_iframes:
                valid_iframes.sort(key=lambda x: x[1], reverse=True)
                return valid_iframes[0][0]
            
            # 3. 查找其他游戏嵌入方式
            game_elements = soup.select(
                '[data-game-url], [data-embed-url], [data-src*="game"], '
                '[class*="embed"], [id*="embed"], [class*="player"], [id*="player"]'
            )
            
            for element in game_elements:
                for attr in ['data-game-url', 'data-embed-url', 'data-src', 'src']:
                    url = element.get(attr)
                    if url and self._is_valid_game_iframe(url, game_url):
                        return urljoin(game_url, url)
            
            # 4. 特殊平台处理
            return self._extract_platform_specific_url(soup, game_url)
            
        except Exception as e:
            logger.warning(f"查找iframe失败 {game_url}: {e}")
            # 对于403错误，尝试基于URL模式推断iframe
            if "403" in str(e) or "Forbidden" in str(e):
                return self._infer_iframe_from_url(game_url)
            return None
    
    def _is_valid_game_iframe(self, iframe_src: str, base_url: str) -> bool:
        """验证iframe URL是否是有效的游戏嵌入（增强版，更严格的过滤）"""
        if not iframe_src:
            return False
        
        # 转换为完整URL
        full_url = urljoin(base_url, iframe_src)
        parsed = urlparse(full_url)
        
        # 🚫 首先过滤明显无效的URL
        if not self._basic_url_validation(full_url, parsed):
            return False
        
        # 🥇 第一优先级：白名单域名（最可信）
        is_whitelisted = any(domain in parsed.netloc or domain in full_url for domain in EMBEDDABLE_DOMAINS)
        if is_whitelisted:
            logger.debug(f"✅ 白名单验证通过: {full_url}")
            return True
        
        # 如果启用严格白名单模式，只接受白名单域名
        if STRICT_WHITELIST:
            logger.debug(f"❌ 严格白名单模式拒绝: {full_url}")
            return False
        
        # 🎮 智能游戏URL检测（无需白名单）
        score = self._calculate_game_url_score(full_url, parsed)
        
        # 如果得分足够高，即使不在白名单中也接受
        is_valid = score >= Config.GAME_URL_SCORE_THRESHOLD
        
        if is_valid:
            logger.info(f"🤖 智能验证通过 (得分: {score}): {full_url}")
        else:
            logger.debug(f"🤖 智能验证失败 (得分: {score}): {full_url}")
        
        return is_valid
    
    def _basic_url_validation(self, full_url: str, parsed) -> bool:
        """基础URL验证，过滤明显无效的URL"""
        url_lower = full_url.lower()
        
        # 🚫 必须是HTTP/HTTPS协议
        if parsed.scheme not in ['http', 'https']:
            logger.debug(f"❌ 协议无效: {parsed.scheme}")
            return False
        
        # 🚫 排除明显不是游戏的iframe
        exclude_patterns = [
            'ads', 'analytics', 'tracking', 'social', 'comment', 'chat',
            'youtube', 'vimeo', 'twitter', 'facebook', 'instagram',
            'discord', 'reddit', 'forum', 'feedback', 'survey',
            'advertisement', 'banner', 'popup', 'cookie', 'gdpr',
            'newsletter', 'signup', 'login', 'register', 'captcha',
            'recaptcha', 'cloudflare', 'error', '404', '403'
        ]
        
        for pattern in exclude_patterns:
            if pattern in url_lower:
                logger.debug(f"❌ 包含排除模式 '{pattern}': {full_url}")
                return False
        
        # 🚫 排除可疑的顶级域名
        suspicious_tlds = ['.tk', '.ml', '.ga', '.cf', '.click', '.download']
        for tld in suspicious_tlds:
            if parsed.netloc.endswith(tld):
                logger.debug(f"❌ 可疑域名后缀 '{tld}': {parsed.netloc}")
                return False
        
        # 🚫 检查URL长度合理性
        if len(full_url) > 500:
            logger.debug(f"❌ URL过长 ({len(full_url)} 字符): {full_url[:100]}...")
            return False
        
        # 🚫 检查域名合理性
        if len(parsed.netloc) > 80 or len(parsed.netloc) < 4:
            logger.debug(f"❌ 域名长度异常: {parsed.netloc}")
            return False
        
        # 🚫 排除localhost和内网地址
        localhost_patterns = ['localhost', '127.0.0.1', '192.168.', '10.0.', '172.16.']
        for pattern in localhost_patterns:
            if pattern in parsed.netloc:
                logger.debug(f"❌ 本地/内网地址: {parsed.netloc}")
                return False
        
        return True
    
    def _calculate_game_url_score(self, full_url: str, parsed) -> int:
        """计算游戏URL的可信度评分（不依赖白名单）"""
        score = 0
        url_lower = full_url.lower()
        domain = parsed.netloc.lower()
        path = parsed.path.lower()
        
        # 🎯 游戏相关路径检测（高分）
        game_paths = [
            '/game/', '/games/', '/play/', '/embed/', '/player/', '/html5/',
            '/swf/', '/flash/', '/unity/', '/webgl/', '/canvas/'
        ]
        
        for pattern in game_paths:
            if pattern in path:
                score += 25
                break  # 只加一次分
        
        # 🎯 游戏相关文件名检测
        game_files = [
            'game.html', 'index.html', 'main.html', 'play.html',
            'game.js', 'main.js', 'app.js', 'bundle.js'
        ]
        
        for filename in game_files:
            if filename in path:
                score += 20
                break
        
        # 🎯 游戏相关域名特征
        game_domain_keywords = [
            'game', 'play', 'arcade', 'html5', 'flash', 'unity',
            'embed', 'cdn', 'assets', 'static', 'media'
        ]
        
        for keyword in game_domain_keywords:
            if keyword in domain:
                score += 15
                break
        
        # 🎯 知名游戏CDN和托管服务检测
        trusted_patterns = [
            '.itch.zone', '.hwcdn.net', '.gamedistribution.com',
            '.armorgames.com', '.kongregate.com', '.newgrounds.com',
            '.crazygames.com', '.poki.com', '.y8.com',
            'cloudfront.net', 'amazonaws.com', 'github.io'
        ]
        
        for pattern in trusted_patterns:
            if pattern in domain:
                score += 30  # 高分，这些是可信的托管服务
                break
        
        # 🎯 HTTPS协议加分
        if parsed.scheme == 'https':
            score += 10
        
        # 🎯 合理的端口（非常见端口减分）
        if parsed.port and parsed.port not in [80, 443, 8080, 3000]:
            score -= 10
        
        # 🎯 查询参数中的游戏标识
        if parsed.query:
            query_lower = parsed.query.lower()
            if any(param in query_lower for param in ['game', 'play', 'embed', 'id=']):
                score += 10
        
        # 🚫 可疑域名特征减分
        suspicious_keywords = [
            'redirect', 'proxy', 'mirror', 'fake', 'spam',
            'ad', 'ads', 'banner', 'popup'
        ]
        
        for keyword in suspicious_keywords:
            if keyword in domain:
                score -= 20
        
        # 🚫 过长的域名可能是可疑的
        if len(domain) > 50:
            score -= 15
        
        # 🚫 包含多个连续数字的域名（可能是临时域名）
        import re
        if re.search(r'\d{4,}', domain):
            score -= 10
        
        return max(0, score)  # 确保分数不为负数
    
    def _calculate_iframe_score(self, iframe_element, iframe_url: str) -> int:
        """计算iframe的可信度分数"""
        score = 0
        
        # URL域名权重
        parsed = urlparse(iframe_url)
        if any(domain in parsed.netloc for domain in EMBEDDABLE_DOMAINS):
            score += 100
        
        # iframe属性检查
        iframe_class = iframe_element.get('class', [])
        iframe_id = iframe_element.get('id', '')
        
        if isinstance(iframe_class, list):
            iframe_class = ' '.join(iframe_class)
        
        attrs_text = f"{iframe_class} {iframe_id}".lower()
        
        # 游戏相关属性加分
        if any(word in attrs_text for word in ['game', 'play', 'embed', 'player']):
            score += 50
        
        # URL路径加分
        if any(word in iframe_url.lower() for word in ['/game/', '/play/', '/embed/']):
            score += 30
        
        # iframe尺寸检查（游戏通常有合理的尺寸）
        width = iframe_element.get('width', '')
        height = iframe_element.get('height', '')
        
        try:
            if width and height:
                w, h = int(width), int(height)
                if 300 <= w <= 1920 and 200 <= h <= 1080:  # 合理的游戏尺寸
                    score += 20
        except:
            pass
        
        return score
    
    def _extract_platform_specific_url(self, soup, base_url: str) -> Optional[str]:
        """特定平台的URL提取逻辑"""
        parsed_base = urlparse(base_url)
        
        # itch.io 特殊处理
        if 'itch.io' in parsed_base.netloc:
            # 查找itch.io的游戏嵌入
            play_buttons = soup.select('a[href*="html"], .button[href*="html"]')
            for button in play_buttons:
                href = button.get('href')
                if href and 'html' in href:
                    return urljoin(base_url, href)
        
        # GameJolt 特殊处理
        elif 'gamejolt.com' in parsed_base.netloc:
            # 查找GameJolt的游戏嵌入
            game_frames = soup.select('[class*="game-embed"], [id*="game-embed"]')
            for frame in game_frames:
                src = frame.get('src') or frame.get('data-src')
                if src:
                    return urljoin(base_url, src)
        
        # Newgrounds 特殊处理
        elif 'newgrounds.com' in parsed_base.netloc:
            # 查找Newgrounds的游戏嵌入
            embed_links = soup.select('a[href*="/portal/view/"]')
            for link in embed_links:
                href = link.get('href')
                if href:
                    return urljoin(base_url, href)
        
        return None
    
    def _get_special_headers(self, url: str) -> Dict[str, str]:
        """为特定网站返回特殊的请求头"""
        headers = get_random_headers()
        parsed = urlparse(url)
        
        # GameJolt 特殊处理
        if 'gamejolt.com' in parsed.netloc:
            headers.update({
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
                'Accept-Encoding': 'gzip, deflate, br',
                'DNT': '1',
                'Connection': 'keep-alive',
                'Cookie': 'frontend=true',  # 模拟前端访问
                'Sec-Fetch-Dest': 'document',
                'Sec-Fetch-Mode': 'navigate',
                'Sec-Fetch-Site': 'none',
                'Pragma': 'no-cache',
                'Cache-Control': 'no-cache'
            })
        
        # itch.io 特殊处理
        elif 'itch.io' in parsed.netloc:
            headers.update({
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Sec-Fetch-Dest': 'document',
                'Sec-Fetch-Mode': 'navigate',
                'Sec-Fetch-Site': 'same-origin'
            })
        
        # Newgrounds 特殊处理
        elif 'newgrounds.com' in parsed.netloc:
            headers.update({
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Referer': 'https://www.newgrounds.com/',
                'Origin': 'https://www.newgrounds.com'
            })
        
        return headers
    
    def _infer_iframe_from_url(self, game_url: str) -> Optional[str]:
        """基于游戏页面URL推断可能的iframe URL"""
        parsed = urlparse(game_url)
        
        try:
            # GameJolt URL模式推断
            if 'gamejolt.com' in parsed.netloc and '/games/' in parsed.path:
                # 从 /games/game-name/id 推断嵌入URL
                path_parts = parsed.path.strip('/').split('/')
                if len(path_parts) >= 3 and path_parts[0] == 'games':
                    game_id = path_parts[-1]
                    # GameJolt的嵌入URL模式
                    embed_url = f"https://gamejolt.net/games/embed/{game_id}"
                    logger.info(f"推断GameJolt iframe: {embed_url}")
                    return embed_url
            
            # itch.io URL模式推断
            elif 'itch.io' in parsed.netloc:
                # 很多itch.io游戏有标准的HTML5嵌入格式
                base_url = f"{parsed.scheme}://{parsed.netloc}"
                if parsed.path:
                    # 尝试添加 /embed 后缀
                    embed_path = parsed.path.rstrip('/') + '/embed'
                    embed_url = f"{base_url}{embed_path}"
                    logger.info(f"推断itch.io iframe: {embed_url}")
                    return embed_url
            
            # Newgrounds URL模式推断
            elif 'newgrounds.com' in parsed.netloc and '/portal/view/' in parsed.path:
                # Newgrounds的嵌入URL通常就是原URL
                logger.info(f"使用Newgrounds原URL: {game_url}")
                return game_url
            
        except Exception as e:
            logger.debug(f"URL模式推断失败: {e}")
        
        return None
    
    def _verify_iframe_playable(self, iframe_url: str) -> bool:
        """验证iframe URL是否真的可以加载游戏"""
        try:
            # 发送HEAD请求检查URL是否可访问
            special_headers = self._get_special_headers(iframe_url)
            response = self._make_request(iframe_url, method='head', headers=special_headers)
            
            if response.status_code != 200:
                logger.debug(f"iframe响应状态: {response.status_code} - {iframe_url}")
                return False
            
            # 检查内容类型
            content_type = response.headers.get('content-type', '').lower()
            
            # HTML内容通常是游戏页面
            if 'text/html' in content_type:
                return True
            
            # 一些游戏直接提供JavaScript或其他内容
            if any(ct in content_type for ct in ['application/javascript', 'text/javascript', 'application/json']):
                return True
            
            logger.debug(f"iframe内容类型: {content_type} - {iframe_url}")
            return False
            
        except Exception as e:
            error_msg = str(e).lower()
            
            # 对于某些特定错误，我们仍然认为URL可能有效
            if any(pattern in error_msg for pattern in ['403', 'forbidden', 'timeout']):
                # 如果是白名单域名，即使403也认为可能有效
                parsed = urlparse(iframe_url)
                if any(domain in parsed.netloc or domain in iframe_url for domain in EMBEDDABLE_DOMAINS):
                    logger.info(f"白名单域名403错误，仍然接受: {iframe_url}")
                    return True
            
            logger.debug(f"验证iframe失败: {e} - {iframe_url}")
            return False

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='游戏管理器 - 统一的游戏数据管理工具')
    parser.add_argument('--action', choices=['clean', 'crawl', 'fix-thumbnails', 'all'], 
                       default='all', help='执行的操作')
    parser.add_argument('--max-games', type=int, default=Config.MAX_GAMES_DEFAULT, help='爬取的最大游戏数量')
    parser.add_argument('--use-proxy', action='store_true', help='启用代理模式（也可通过环境变量 USE_PROXY=true 配置）')
    parser.add_argument('--strict-whitelist', action='store_true', help='启用严格白名单模式，只接受预定义域名')
    parser.add_argument('--show-config', action='store_true', help='显示当前配置并退出')
    
    args = parser.parse_args()
    
    # 从命令行参数更新配置
    Config.update_from_args(args)
    
    # 如果只是显示配置，则输出后退出
    if args.show_config:
        Config.print_status()
        return
    
    manager = GameManager()
    
    if args.action == 'clean':
        logger.info("🧹 开始清理游戏数据...")
        games = manager.clean_games()
        games = manager.remove_duplicates(games)
        manager.write_games_file(games)
        
    elif args.action == 'crawl':
        logger.info(f"🕷️ 开始爬取新游戏（最多{args.max_games}个）...")
        new_games = manager.crawl_new_games(args.max_games)
        existing_games = manager.read_games_file()
        all_games = existing_games + new_games
        all_games = manager.remove_duplicates(all_games)
        manager.write_games_file(all_games)
        
    elif args.action == 'fix-thumbnails':
        logger.info("🖼️ 开始修复游戏封面...")
        games = manager.read_games_file()
        games = manager.fix_thumbnails(games)
        manager.write_games_file(games)
        
    elif args.action == 'all':
        logger.info("🔄 开始全面管理...")
        # 1. 清理现有数据
        games = manager.clean_games()
        games = manager.remove_duplicates(games)
        
        # 2. 修复缩略图
        games = manager.fix_thumbnails(games)
        
        # 3. 爬取新游戏
        new_games = manager.crawl_new_games(args.max_games)
        all_games = games + new_games
        all_games = manager.remove_duplicates(all_games)
        
        # 4. 再次修复缩略图
        all_games = manager.fix_thumbnails(all_games)
        
        # 5. 保存结果
        manager.write_games_file(all_games)
    
    logger.info("✅ 游戏管理器执行完成！")

if __name__ == '__main__':
    main() 