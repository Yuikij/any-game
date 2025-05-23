#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
离线演示脚本 - 模拟游戏爬虫功能，无需网络连接
用于演示爬虫的核心数据处理逻辑
"""

import json
import os
from datetime import datetime
from typing import List, Dict

# 项目配置
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GAMES_DATA_FILE = os.path.join(PROJECT_ROOT, 'src', 'data', 'games.ts')

# 分类映射
CATEGORY_MAPPING = {
    'puzzle': '益智',
    'action': '动作', 
    'adventure': '冒险',
    'arcade': '休闲',
    'casual': '休闲',
    'strategy': '策略',
    'sports': '体育'
}

# 分类ID映射
CATEGORY_ID_MAPPING = {
    '休闲': '1',
    '益智': '2', 
    '动作': '3',
    '卡牌': '4',
    '体育': '5',
    '棋盘': '6'
}

def generate_mock_games() -> List[Dict]:
    """生成模拟的游戏数据"""
    mock_games = [
        {
            'title': 'Super Puzzle Adventure',
            'description': '一款令人上瘾的益智游戏，挑战你的逻辑思维能力',
            'category': '益智',
            'thumbnail_url': 'https://example.com/thumb1.jpg',
            'game_url': 'https://example.com/game1',
            'type': 'iframe',
            'game_data': {'iframe_url': 'https://example.com/game1/play'}
        },
        {
            'title': 'Racing Thunder',
            'description': '高速赛车游戏，体验极速驾驶的刺激感受',
            'category': '动作',
            'thumbnail_url': 'https://example.com/thumb2.jpg',
            'game_url': 'https://example.com/game2',
            'type': 'iframe',
            'game_data': {'iframe_url': 'https://example.com/game2/play'}
        },
        {
            'title': 'Casual Match 3',
            'description': '轻松的三消游戏，适合所有年龄段的玩家',
            'category': '休闲',
            'thumbnail_url': 'https://example.com/thumb3.jpg',
            'game_url': 'https://example.com/game3',
            'type': 'static',
            'game_data': {'static_url': 'https://example.com/game3/index.html'}
        },
        {
            'title': 'Strategy Empire',
            'description': '建立你的帝国，征服整个世界的策略游戏',
            'category': '策略',
            'thumbnail_url': 'https://example.com/thumb4.jpg',
            'game_url': 'https://example.com/game4',
            'type': 'iframe',
            'game_data': {'iframe_url': 'https://example.com/game4/play'}
        },
        {
            'title': 'Sports Championship',
            'description': '多种体育项目的综合竞技游戏',
            'category': '体育',
            'thumbnail_url': 'https://example.com/thumb5.jpg',
            'game_url': 'https://example.com/game5',
            'type': 'static',
            'game_data': {'static_url': 'https://example.com/game5/index.html'}
        }
    ]
    
    return mock_games

def generate_tags(game: Dict) -> List[str]:
    """为游戏生成标签"""
    tags = [game['category']]
    
    title_lower = game['title'].lower()
    desc_lower = game.get('description', '').lower()
    
    # 根据标题和描述添加标签
    tag_keywords = {
        '多人': ['multiplayer', 'multi', '多人', '联机'],
        '单人': ['single', 'solo', '单人'],
        '3D': ['3d', '三维'],
        '2D': ['2d', '二维', 'pixel'],
        '复古': ['retro', 'classic', '经典', '怀旧'],
        '可爱': ['cute', 'kawaii', '可爱', '萌'],
        '困难': ['hard', 'difficult', '困难', '挑战'],
        '简单': ['easy', 'simple', '简单', '轻松', 'casual']
    }
    
    for tag, keywords in tag_keywords.items():
        if any(keyword in title_lower or keyword in desc_lower for keyword in keywords):
            tags.append(tag)
    
    return tags[:5]  # 限制标签数量

def process_games(games: List[Dict]) -> List[Dict]:
    """处理游戏数据，生成最终的游戏数据"""
    processed_games = []
    
    for i, game in enumerate(games):
        # 生成游戏ID（从10开始避免与现有游戏冲突）
        game_id = str(10 + i)
        
        # 获取分类ID
        category_id = CATEGORY_ID_MAPPING.get(game['category'], '1')
        
        # 构建游戏数据
        game_data = {
            'id': game_id,
            'title': game['title'],
            'description': game['description'],
            'category': game['category'],
            'categoryId': category_id,
            'thumbnail': f'/games/thumbnails/demo_{game_id}.jpg',
            'path': f'/games/{game_id}',
            'featured': i == 0,  # 第一个游戏设为特色
            'type': game['type'],
            'addedAt': datetime.now().strftime('%Y-%m-%d'),
            'tags': generate_tags(game)
        }
        
        # 添加类型特定的数据
        if game['type'] == 'iframe':
            game_data['iframeUrl'] = game['game_data']['iframe_url']
        else:
            game_data['staticPath'] = game['game_data'].get('static_url', f'/games/{game_id}/index.html')
        
        processed_games.append(game_data)
        print(f"✓ 处理游戏: {game_data['title']} ({game_data['type']})")
    
    return processed_games

def save_games_to_file(new_games: List[Dict]):
    """将新游戏保存到games.ts文件"""
    try:
        # 读取现有文件
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
        
        # 如果文件存在，在现有games数组中添加新游戏
        if content and 'export const games: Game[] = [' in content:
            # 在最后一个游戏后添加新游戏
            insert_pos = content.rfind('};')
            if insert_pos != -1:
                # 找到最后一个游戏对象的结束位置
                insert_pos = content.find('\n', insert_pos) + 1
                new_content = content[:insert_pos] + new_games_code + content[insert_pos:]
            else:
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
        
        print(f"✓ 成功保存 {len(new_games)} 个新游戏到 {GAMES_DATA_FILE}")
        
    except Exception as e:
        print(f"✗ 保存游戏数据失败: {e}")

def main():
    """主函数"""
    print("🎮 离线游戏爬虫演示")
    print("=" * 50)
    
    print("\n📋 步骤1: 生成模拟游戏数据...")
    mock_games = generate_mock_games()
    print(f"✓ 生成了 {len(mock_games)} 个模拟游戏")
    
    print("\n🔄 步骤2: 处理游戏数据...")
    processed_games = process_games(mock_games)
    
    print("\n💾 步骤3: 保存到文件...")
    save_games_to_file(processed_games)
    
    print("\n🎉 演示完成！")
    print(f"📁 请检查文件: {GAMES_DATA_FILE}")
    print("\n📊 添加的游戏统计:")
    
    category_count = {}
    for game in processed_games:
        category = game['category']
        category_count[category] = category_count.get(category, 0) + 1
    
    for category, count in category_count.items():
        print(f"  • {category}: {count} 个游戏")
    
    print(f"\n总计: {len(processed_games)} 个游戏")

if __name__ == '__main__':
    main() 