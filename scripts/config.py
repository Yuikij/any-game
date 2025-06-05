#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
游戏管理器配置文件
所有脚本共享的配置项
"""

import os

# ========================================================================================
# 🔧 核心配置区域 - 可以直接在这里修改配置
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
    CRAWL_DELAY_MIN = 2.0     # 📝 最小延迟（秒）- 增加以避免429错误
    CRAWL_DELAY_MAX = 5.0     # 📝 最大延迟（秒）- 增加以避免429错误
    REQUEST_TIMEOUT = 15      # 📝 请求超时时间（秒）
    RETRY_ATTEMPTS = 3        # 📝 重试次数
    
    # 🚦 特定平台延迟配置（避免429错误）
    PLATFORM_DELAYS = {
        'itch.io': (4.0, 8.0),      # itch.io需要更长延迟
        'gamejolt.com': (3.0, 6.0), # GameJolt中等延迟
        'newgrounds.com': (2.0, 4.0), # Newgrounds较短延迟
        'default': (2.0, 5.0)       # 默认延迟
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

# 初始化配置
Config.load_from_env()

# 快捷访问（向后兼容）
def get_config():
    """获取配置实例"""
    return Config

def is_proxy_enabled():
    """检查是否启用代理"""
    return Config.USE_PROXY

def is_strict_whitelist():
    """检查是否启用严格白名单模式"""
    return Config.STRICT_WHITELIST

def get_proxy_settings():
    """获取代理设置"""
    if Config.USE_PROXY:
        return {
            'http': f'http://{Config.PROXY_HOST}:{Config.PROXY_PORT}',
            'https': f'http://{Config.PROXY_HOST}:{Config.PROXY_PORT}'
        }
    return None

# 导出常用配置（向后兼容）
USE_PROXY = Config.USE_PROXY
PROXY_HOST = Config.PROXY_HOST
PROXY_PORT = Config.PROXY_PORT
STRICT_WHITELIST = Config.STRICT_WHITELIST
SERPAPI_KEY = Config.SERPAPI_KEY
GOOGLE_API_KEY = Config.GOOGLE_API_KEY
GOOGLE_CX = Config.GOOGLE_CX 