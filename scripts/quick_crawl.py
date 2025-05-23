#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
快速游戏爬虫脚本 - 简化版本，用于快速测试和小规模爬取
"""

import requests
from bs4 import BeautifulSoup
import json
import os
import re
from urllib.parse import urljoin
from datetime import datetime

# 项目配置
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GAMES_DATA_FILE = os.path.join(PROJECT_ROOT, 'src', 'data', 'games.ts')

# 简化的种子URL列表
QUICK_URLS = [
    'https://itch.io/games/html5',
    'https://www.newgrounds.com/games/browse',
]

# 请求头
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
}

# 分类映射
CATEGORIES = {
    'puzzle': '益智',
    'action': '动作',
    'arcade': '休闲',
    'casual': '休闲',
    'strategy': '策略',
    'sports': '体育'
}

def fetch_page(url):
    """获取网页内容"""
    try:
        print(f"正在获取: {url}")
        response = requests.get(url, headers=HEADERS, timeout=10)
        response.raise_for_status()
        return BeautifulSoup(response.text, 'html.parser')
    except Exception as e:
        print(f"获取失败 {url}: {e}")
        return None

def extract_games_from_itch(soup, base_url):
    """从itch.io提取游戏"""
    games = []
    for item in soup.select('.game_cell')[:5]:  # 限制5个游戏
        try:
            title_elem = item.select_one('.title a')
            if not title_elem:
                continue
            
            title = title_elem.get_text(strip=True)
            game_url = urljoin(base_url, title_elem['href'])
            
            # 获取缩略图
            img_elem = item.select_one('img')
            thumbnail = urljoin(base_url, img_elem['src']) if img_elem else None
            
            # 获取描述
            desc_elem = item.select_one('.game_text')
            description = desc_elem.get_text(strip=True) if desc_elem else f"一款有趣的{title}游戏"
            
            games.append({
                'title': title,
                'description': description[:100] + '...' if len(description) > 100 else description,
                'category': '休闲',
                'thumbnail_url': thumbnail,
                'game_url': game_url,
                'type': 'iframe'
            })
            print(f"提取游戏: {title}")
            
        except Exception as e:
            print(f"提取游戏失败: {e}")
            continue
    
    return games

def extract_games_from_newgrounds(soup, base_url):
    """从Newgrounds提取游戏"""
    games = []
    for item in soup.select('.item-portalitem')[:5]:  # 限制5个游戏
        try:
            title_elem = item.select_one('.item-details h4 a')
            if not title_elem:
                continue
            
            title = title_elem.get_text(strip=True)
            game_url = urljoin(base_url, title_elem['href'])
            
            # 获取缩略图
            img_elem = item.select_one('img')
            thumbnail = urljoin(base_url, img_elem['src']) if img_elem else None
            
            games.append({
                'title': title,
                'description': f"来自Newgrounds的{title}游戏",
                'category': '动作',
                'thumbnail_url': thumbnail,
                'game_url': game_url,
                'type': 'iframe'
            })
            print(f"提取游戏: {title}")
            
        except Exception as e:
            print(f"提取游戏失败: {e}")
            continue
    
    return games

def process_games(games):
    """处理游戏数据"""
    processed = []
    
    for i, game in enumerate(games):
        game_id = str(10 + i)  # 从ID 10开始，避免与现有游戏冲突
        
        processed_game = {
            'id': game_id,
            'title': game['title'][:50],  # 限制标题长度
            'description': game['description'],
            'category': game['category'],
            'categoryId': '1' if game['category'] == '休闲' else '3',  # 休闲或动作
            'thumbnail': f'/games/thumbnails/game_{game_id}.jpg',
            'path': f'/games/{game_id}',
            'featured': False,
            'type': game['type'],
            'iframeUrl': game['game_url'],
            'addedAt': datetime.now().strftime('%Y-%m-%d'),
            'tags': [game['category'], '在线']
        }
        
        processed.append(processed_game)
    
    return processed

def save_to_file(games):
    """保存游戏到文件"""
    if not games:
        print("没有游戏数据需要保存")
        return
    
    # 生成新游戏代码
    games_code = ""
    for game in games:
        # 预处理字符串，避免在f-string中使用反斜杠
        title_escaped = game['title'].replace("'", "\\'")
        desc_escaped = game['description'].replace("'", "\\'")
        
        games_code += f"""  {{
    id: '{game['id']}',
    title: '{title_escaped}',
    description: '{desc_escaped}',
    category: '{game['category']}',
    categoryId: '{game['categoryId']}',
    thumbnail: '{game['thumbnail']}',
    path: '{game['path']}',
    featured: {str(game['featured']).lower()},
    type: '{game['type']}',
    iframeUrl: '{game['iframeUrl']}',
    addedAt: '{game['addedAt']}',
    tags: {json.dumps(game['tags'], ensure_ascii=False)}
  }},
"""
    
    # 读取现有文件
    if os.path.exists(GAMES_DATA_FILE):
        with open(GAMES_DATA_FILE, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 在games数组末尾添加新游戏
        insert_pos = content.rfind('};')
        if insert_pos != -1:
            insert_pos = content.find('\n', insert_pos) + 1
            new_content = content[:insert_pos] + games_code + content[insert_pos:]
        else:
            new_content = content + games_code
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
        f.write(new_content)
    
    print(f"成功保存 {len(games)} 个游戏到 {GAMES_DATA_FILE}")

def main():
    """主函数"""
    print("开始快速爬取游戏...")
    
    all_games = []
    
    # 爬取itch.io
    soup = fetch_page(QUICK_URLS[0])
    if soup:
        games = extract_games_from_itch(soup, QUICK_URLS[0])
        all_games.extend(games)
    
    # 爬取Newgrounds
    soup = fetch_page(QUICK_URLS[1])
    if soup:
        games = extract_games_from_newgrounds(soup, QUICK_URLS[1])
        all_games.extend(games)
    
    print(f"共找到 {len(all_games)} 个游戏")
    
    # 处理游戏数据
    processed_games = process_games(all_games)
    
    # 保存到文件
    save_to_file(processed_games)
    
    print("快速爬取完成！")

if __name__ == '__main__':
    main() 