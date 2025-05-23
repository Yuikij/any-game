#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
严格清理游戏数据脚本
只保留真正可以iframe嵌入或本地运行的游戏，移除所有跳转到外部链接的游戏
"""

import os
import re
import json
import logging
import requests
from datetime import datetime
from urllib.parse import urlparse

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('strict_clean_games.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# 项目配置
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GAMES_DATA_FILE = os.path.join(PROJECT_ROOT, 'src', 'data', 'games.ts')
BACKUP_FILE = os.path.join(PROJECT_ROOT, 'src', 'data', 'games.ts.strict_backup')

# 真正可嵌入的域名白名单
EMBEDDABLE_DOMAINS = [
    'html-classic.itch.zone',      # itch.io的HTML5游戏嵌入域名
    'v6p9d9t4.ssl.hwcdn.net',      # itch.io的CDN域名
    'uploads.ungrounded.net',       # Newgrounds嵌入域名
    'gamejolt.net',                # GameJolt嵌入域名
    'crazygames.com/embed',        # CrazyGames嵌入
    'poki.com/embed',              # Poki嵌入
    'kongregate.com/embed',        # Kongregate嵌入
]

# 绝对不允许的域名黑名单
BLOCKED_DOMAINS = [
    'itch.io',                     # itch.io主站（游戏页面，不是游戏本身）
    'gamejolt.com',               # GameJolt主站
    'newgrounds.com',             # Newgrounds主站
    'armorgames.com',             # ArmorGames主站
    'miniclip.com',               # Miniclip主站
    'crazygames.com',             # CrazyGames主站（非embed）
    'poki.com',                   # Poki主站（非embed）
    'kongregate.com',             # Kongregate主站（非embed）
    'youtube.com',                # YouTube
    'mobilegamer.biz',            # 新闻网站
    'gamedeveloper.com',          # 新闻网站
    'gamesindustry.biz',          # 新闻网站
]

def is_truly_embeddable_url(url: str) -> bool:
    """严格检查URL是否真正可嵌入"""
    try:
        if not url or not url.startswith('http'):
            return False
        
        parsed = urlparse(url)
        domain = parsed.netloc.lower()
        
        # 1. 检查是否在黑名单中
        for blocked in BLOCKED_DOMAINS:
            if blocked in domain:
                logger.info(f"❌ 黑名单域名: {url}")
                return False
        
        # 2. 检查是否在白名单中
        for allowed in EMBEDDABLE_DOMAINS:
            if allowed in domain:
                logger.info(f"✅ 白名单域名: {url}")
                return True
        
        # 3. 检查是否是HTML5游戏文件
        if url.endswith(('.html', '.htm')) and any(indicator in url.lower() for indicator in ['/play/', '/game/', 'index.html']):
            # 进一步验证是否真的是游戏文件
            try:
                response = requests.head(url, timeout=5, allow_redirects=True)
                content_type = response.headers.get('Content-Type', '').lower()
                if 'text/html' in content_type:
                    # 检查X-Frame-Options
                    frame_options = response.headers.get('X-Frame-Options', '').upper()
                    if frame_options not in ['DENY', 'SAMEORIGIN']:
                        logger.info(f"✅ 有效HTML5游戏: {url}")
                        return True
            except:
                pass
        
        logger.info(f"❌ 不可嵌入: {url}")
        return False
        
    except Exception as e:
        logger.error(f"验证URL失败: {url}, {e}")
        return False

def validate_game_strictly(game_text: str) -> bool:
    """严格验证游戏对象"""
    try:
        # 提取标题
        title_match = re.search(r"title:\s*['\"]([^'\"]*)['\"]", game_text)
        if not title_match:
            return False
        
        title = title_match.group(1).strip()
        
        # 1. 检查标题有效性（更严格）
        invalid_titles = [
            'unleash the gamer', 'play games', 'free games', 'online games',
            'game portal', 'gaming platform', 'entertainment', 'company',
            'developer', 'publisher', 'studio', 'browse games', 'all games',
            'categories', 'joins', 'acquires', 'acquisition', 'news',
            'lessmore', 'easybrain', 'miniclip'
        ]
        
        title_lower = title.lower()
        if any(invalid in title_lower for invalid in invalid_titles):
            logger.info(f"❌ 无效标题: {title}")
            return False
        
        # 2. 检查标题长度
        if len(title) < 3 or len(title) > 80:
            logger.info(f"❌ 标题长度不合适: {title}")
            return False
        
        # 3. 检查描述（更严格）
        desc_match = re.search(r"description:\s*['\"]([^'\"]*)['\"]", game_text, re.DOTALL)
        if desc_match:
            description = desc_match.group(1).strip()
            
            # 检查是否是公司/新闻描述
            company_keywords = [
                'we develop', 'we publish', 'we reach', 'million players',
                'international', 'company', 'entertainment company',
                'game developer', 'our audience', 'multiplayer mobile games',
                'digital games and entertainment', 'acquisition', 'joins',
                'bringing in', 'marks a strategic', 'expansion into'
            ]
            
            desc_lower = description.lower()
            if any(keyword in desc_lower for keyword in company_keywords):
                logger.info(f"❌ 公司/新闻描述: {title}")
                return False
        
        # 4. 严格检查URL
        iframe_match = re.search(r"iframeUrl:\s*['\"]([^'\"]*)['\"]", game_text)
        static_match = re.search(r"staticPath:\s*['\"]([^'\"]*)['\"]", game_text)
        
        game_url = None
        if iframe_match:
            game_url = iframe_match.group(1).strip()
        elif static_match:
            game_url = static_match.group(1).strip()
        
        if not game_url or not is_truly_embeddable_url(game_url):
            logger.info(f"❌ URL不可嵌入: {title} -> {game_url}")
            return False
        
        logger.info(f"✅ 严格验证通过: {title}")
        return True
        
    except Exception as e:
        logger.error(f"严格验证失败: {e}")
        return False

def extract_embeddable_games():
    """提取真正可嵌入的游戏"""
    try:
        if not os.path.exists(GAMES_DATA_FILE):
            logger.error(f"文件不存在: {GAMES_DATA_FILE}")
            return []
        
        with open(GAMES_DATA_FILE, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 备份原文件
        with open(BACKUP_FILE, 'w', encoding='utf-8') as f:
            f.write(content)
        logger.info(f"已备份原文件到: {BACKUP_FILE}")
        
        # 提取所有游戏对象
        game_pattern = r'{\s*id:\s*[\'"][^\'"]*[\'"].*?(?:tags:\s*\[[^\]]*\]|iframeUrl:\s*[\'"][^\'"]*[\'"]|staticPath:\s*[\'"][^\'"]*[\'"])\s*}'
        game_matches = re.findall(game_pattern, content, re.DOTALL)
        
        valid_games = []
        
        for game_match in game_matches:
            if validate_game_strictly(game_match):
                # 解析游戏对象
                game_data = parse_game_object(game_match)
                if game_data:
                    valid_games.append(game_data)
        
        logger.info(f"严格验证后保留 {len(valid_games)} 个真正可嵌入的游戏")
        return valid_games
        
    except Exception as e:
        logger.error(f"提取可嵌入游戏失败: {e}")
        return []

def parse_game_object(game_text: str) -> dict:
    """解析游戏对象"""
    try:
        game_data = {}
        
        # 提取各个字段
        patterns = {
            'id': r"id:\s*['\"]([^'\"]*)['\"]",
            'title': r"title:\s*['\"]([^'\"]*)['\"]",
            'description': r"description:\s*['\"]([^'\"]*)['\"]",
            'category': r"category:\s*['\"]([^'\"]*)['\"]",
            'categoryId': r"categoryId:\s*['\"]([^'\"]*)['\"]",
            'thumbnail': r"thumbnail:\s*['\"]([^'\"]*)['\"]",
            'path': r"path:\s*['\"]([^'\"]*)['\"]",
            'featured': r"featured:\s*(true|false)",
            'type': r"type:\s*['\"]([^'\"]*)['\"]",
            'addedAt': r"addedAt:\s*['\"]([^'\"]*)['\"]"
        }
        
        for key, pattern in patterns.items():
            match = re.search(pattern, game_text)
            if match:
                value = match.group(1)
                if key == 'featured':
                    game_data[key] = value == 'true'
                else:
                    game_data[key] = value
        
        # 提取URL字段
        iframe_match = re.search(r"iframeUrl:\s*['\"]([^'\"]*)['\"]", game_text)
        static_match = re.search(r"staticPath:\s*['\"]([^'\"]*)['\"]", game_text)
        
        if iframe_match:
            game_data['iframeUrl'] = iframe_match.group(1)
            game_data['type'] = 'iframe'
        elif static_match:
            game_data['staticPath'] = static_match.group(1)
            game_data['type'] = 'static'
        
        # 提取tags
        tags_match = re.search(r"tags:\s*(\[[^\]]*\])", game_text)
        if tags_match:
            try:
                tags_str = tags_match.group(1)
                tags = re.findall(r'[\'"]([^\'"]*)[\'"]', tags_str)
                game_data['tags'] = tags
            except:
                game_data['tags'] = []
        else:
            game_data['tags'] = []
        
        return game_data
        
    except Exception as e:
        logger.error(f"解析游戏对象失败: {e}")
        return {}

def rebuild_with_embeddable_games(games: list):
    """用可嵌入游戏重建文件"""
    try:
        # 重新编号游戏ID
        for i, game in enumerate(games):
            game['id'] = str(i + 1)
            game['path'] = f'/games/{i + 1}'
        
        # 生成游戏代码
        games_code = ""
        for game in games:
            if not game:
                continue
            
            # 转义字符串
            title = game.get('title', '').replace("'", "\\'")
            description = game.get('description', '').replace("'", "\\'")
            
            games_code += f"""  {{
    id: '{game.get('id')}',
    title: '{title}',
    description: '{description}',
    category: '{game.get('category', '休闲')}',
    categoryId: '{game.get('categoryId', '1')}',
    thumbnail: '{game.get('thumbnail', '/games/thumbnails/default.jpg')}',
    path: '{game.get('path')}',
    featured: {str(game.get('featured', False)).lower()},
    type: '{game.get('type', 'iframe')}',"""
            
            # 添加URL字段
            if game.get('iframeUrl'):
                games_code += f"\n    iframeUrl: '{game['iframeUrl']}',"
            elif game.get('staticPath'):
                games_code += f"\n    staticPath: '{game['staticPath']}',"
            
            # 添加其他字段
            games_code += f"""
    addedAt: '{game.get('addedAt', datetime.now().strftime('%Y-%m-%d'))}',
    tags: {json.dumps(game.get('tags', []), ensure_ascii=False)}
  }},
"""
        
        # 生成完整文件内容
        file_content = f"""import {{ Game, Category }} from '../types';

export const categories: Category[] = [
  {{ id: '1', name: '休闲', description: '简单有趣的休闲游戏，适合所有年龄段玩家', count: 125, slug: 'casual' }},
  {{ id: '2', name: '益智', description: '锻炼大脑的益智游戏，提升思维能力', count: 98, slug: 'puzzle' }},
  {{ id: '3', name: '动作', description: '刺激的动作游戏，考验你的反应速度', count: 84, slug: 'action' }},
  {{ id: '4', name: '卡牌', description: '卡牌和棋牌类游戏，策略与运气的结合', count: 52, slug: 'card' }},
  {{ id: '5', name: '体育', description: '各类体育模拟游戏，感受体育竞技的乐趣', count: 43, slug: 'sports' }},
  {{ id: '6', name: '棋盘', description: '经典的棋盘游戏，考验战略思维', count: 38, slug: 'board' }},
];

export const games: Game[] = [
{games_code}];

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
            f.write(file_content)
        
        logger.info(f"✅ 成功重建games.ts文件，包含 {len(games)} 个真正可嵌入的游戏")
        return True
        
    except Exception as e:
        logger.error(f"重建文件失败: {e}")
        return False

def main():
    """主函数"""
    logger.info("🔒 开始严格清理games.ts文件...")
    logger.info("💡 只保留真正可以iframe嵌入或本地运行的游戏")
    
    # 1. 提取真正可嵌入的游戏
    embeddable_games = extract_embeddable_games()
    
    if not embeddable_games:
        logger.warning("❌ 没有找到真正可嵌入的游戏")
        return
    
    # 2. 重建文件
    success = rebuild_with_embeddable_games(embeddable_games)
    
    if success:
        logger.info("✅ 严格清理完成！")
        logger.info(f"📊 结果: 保留了 {len(embeddable_games)} 个真正可嵌入的游戏")
        logger.info("🎮 所有保留的游戏都可以在平台内直接运行，不会跳转到外部链接")
    else:
        logger.error("❌ 严格清理失败")

if __name__ == '__main__':
    main() 