#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
移除重复游戏脚本
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
        logging.FileHandler('remove_duplicates.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# 项目配置
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GAMES_DATA_FILE = os.path.join(PROJECT_ROOT, 'src', 'data', 'games.ts')

def remove_duplicate_games():
    """移除重复的游戏"""
    try:
        with open(GAMES_DATA_FILE, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 提取所有游戏对象
        game_pattern = r'{\s*id:\s*[\'"][^\'"]*[\'"].*?(?:tags:\s*\[[^\]]*\]|iframeUrl:\s*[\'"][^\'"]*[\'"]|staticPath:\s*[\'"][^\'"]*[\'"])\s*}'
        game_matches = re.findall(game_pattern, content, re.DOTALL)
        
        unique_games = []
        seen_titles = set()
        seen_urls = set()
        
        for game_match in game_matches:
            # 提取标题和URL
            title_match = re.search(r"title:\s*['\"]([^'\"]*)['\"]", game_match)
            url_match = re.search(r"(?:iframeUrl|staticPath):\s*['\"]([^'\"]*)['\"]", game_match)
            
            if not title_match:
                continue
            
            title = title_match.group(1).strip()
            url = url_match.group(1).strip() if url_match else ""
            
            # 检查是否重复
            title_key = title.lower()
            if title_key in seen_titles or url in seen_urls:
                logger.info(f"❌ 跳过重复游戏: {title}")
                continue
            
            seen_titles.add(title_key)
            if url:
                seen_urls.add(url)
            
            # 解析游戏对象
            game_data = parse_game_object(game_match)
            if game_data:
                unique_games.append(game_data)
                logger.info(f"✅ 保留游戏: {title}")
        
        logger.info(f"去重后保留 {len(unique_games)} 个游戏")
        return unique_games
        
    except Exception as e:
        logger.error(f"移除重复游戏失败: {e}")
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

def rebuild_games_file(games: list):
    """重建games.ts文件"""
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
        
        logger.info(f"✅ 成功重建games.ts文件，包含 {len(games)} 个去重后的游戏")
        return True
        
    except Exception as e:
        logger.error(f"重建文件失败: {e}")
        return False

def main():
    """主函数"""
    logger.info("🔄 开始移除重复游戏...")
    
    # 1. 移除重复游戏
    unique_games = remove_duplicate_games()
    
    if not unique_games:
        logger.warning("❌ 没有找到有效的游戏")
        return
    
    # 2. 重建文件
    success = rebuild_games_file(unique_games)
    
    if success:
        logger.info("✅ 去重完成！")
        logger.info(f"📊 结果: 保留了 {len(unique_games)} 个唯一游戏")
    else:
        logger.error("❌ 去重失败")

if __name__ == '__main__':
    main() 