#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
重建games.ts文件脚本
从头开始创建一个干净的games.ts文件，只包含有效的游戏数据
"""

import os
import re
import json
import logging
from datetime import datetime

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('rebuild_games.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# 项目配置
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GAMES_DATA_FILE = os.path.join(PROJECT_ROOT, 'src', 'data', 'games.ts')
BACKUP_FILE = os.path.join(PROJECT_ROOT, 'src', 'data', 'games.ts.rebuild_backup')

def extract_valid_games():
    """从现有文件中提取有效的游戏数据"""
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
            # 提取游戏信息
            title_match = re.search(r"title:\s*['\"]([^'\"]*)['\"]", game_match)
            if not title_match:
                continue
            
            title = title_match.group(1).strip()
            
            # 验证游戏有效性
            if is_valid_game(game_match, title):
                valid_games.append(parse_game_object(game_match))
        
        logger.info(f"提取到 {len(valid_games)} 个有效游戏")
        return valid_games
        
    except Exception as e:
        logger.error(f"提取游戏数据失败: {e}")
        return []

def is_valid_game(game_text: str, title: str) -> bool:
    """验证游戏是否有效"""
    try:
        # 检查标题有效性
        invalid_titles = [
            'unleash the gamer', 'play games', 'free games', 'online games',
            'game portal', 'gaming platform', 'entertainment', 'company',
            'developer', 'publisher', 'studio', 'browse games', 'all games'
        ]
        
        title_lower = title.lower()
        if any(invalid in title_lower for invalid in invalid_titles):
            logger.info(f"❌ 无效标题: {title}")
            return False
        
        # 检查标题长度
        if len(title) < 3 or len(title) > 100:
            logger.info(f"❌ 标题长度不合适: {title}")
            return False
        
        # 检查描述
        desc_match = re.search(r"description:\s*['\"]([^'\"]*)['\"]", game_text, re.DOTALL)
        if desc_match:
            description = desc_match.group(1).strip()
            company_keywords = [
                'we develop', 'we publish', 'we reach', 'million players',
                'international', 'company', 'entertainment company',
                'game developer', 'our audience', 'multiplayer mobile games',
                'digital games and entertainment'
            ]
            
            desc_lower = description.lower()
            if any(keyword in desc_lower for keyword in company_keywords):
                logger.info(f"❌ 公司介绍: {title}")
                return False
        
        # 检查URL
        url_match = re.search(r"(?:staticPath|iframeUrl):\s*['\"]([^'\"]*)['\"]", game_text)
        if url_match:
            game_url = url_match.group(1).strip()
            invalid_url_patterns = [
                '/games$', '/games/$', 'miniclip.com/games$',
                'itch.io/games$', 'gamejolt.com/games$', 'newgrounds.com/games$',
                '/browse$', '/category$', '/tag/$', 'youtube.com/embed'
            ]
            
            for pattern in invalid_url_patterns:
                if re.search(pattern, game_url, re.IGNORECASE):
                    logger.info(f"❌ 无效URL: {title} -> {game_url}")
                    return False
        
        logger.info(f"✅ 有效游戏: {title}")
        return True
        
    except Exception as e:
        logger.error(f"验证游戏失败: {e}")
        return False

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
        elif static_match:
            game_data['staticPath'] = static_match.group(1)
        
        # 提取tags
        tags_match = re.search(r"tags:\s*(\[[^\]]*\])", game_text)
        if tags_match:
            try:
                tags_str = tags_match.group(1)
                # 简单解析tags数组
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

def rebuild_games_file(games: list):
    """重建games.ts文件"""
    try:
        # 生成游戏代码
        games_code = ""
        for i, game in enumerate(games):
            if not game:
                continue
            
            # 转义字符串
            title = game.get('title', '').replace("'", "\\'")
            description = game.get('description', '').replace("'", "\\'")
            
            games_code += f"""  {{
    id: '{game.get('id', str(i+1))}',
    title: '{title}',
    description: '{description}',
    category: '{game.get('category', '休闲')}',
    categoryId: '{game.get('categoryId', '1')}',
    thumbnail: '{game.get('thumbnail', '/games/thumbnails/default.jpg')}',
    path: '{game.get('path', f'/games/{game.get("id", str(i+1))}')}',
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
        
        logger.info(f"✅ 成功重建games.ts文件，包含 {len(games)} 个游戏")
        return True
        
    except Exception as e:
        logger.error(f"重建文件失败: {e}")
        return False

def main():
    """主函数"""
    logger.info("🔨 开始重建games.ts文件...")
    
    # 1. 提取有效游戏
    valid_games = extract_valid_games()
    
    if not valid_games:
        logger.warning("没有找到有效的游戏数据")
        return
    
    # 2. 重建文件
    success = rebuild_games_file(valid_games)
    
    if success:
        logger.info("✅ games.ts文件重建完成！")
        logger.info(f"📊 结果: 保留了 {len(valid_games)} 个有效游戏")
        logger.info("💡 提示: 文件现在只包含真正的游戏，格式完全正确")
    else:
        logger.error("❌ 文件重建失败")

if __name__ == '__main__':
    main() 