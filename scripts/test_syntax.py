#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
语法测试脚本 - 验证f-string修复是否正确
"""

import json
from datetime import datetime

def test_game_data_generation():
    """测试游戏数据生成"""
    
    # 模拟游戏数据
    test_games = [
        {
            'id': '10',
            'title': "Test Game's Adventure",  # 包含单引号
            'description': "This is a test game with 'quotes' and special characters",
            'category': '休闲',
            'categoryId': '1',
            'thumbnail': '/games/thumbnails/test.jpg',
            'path': '/games/10',
            'featured': False,
            'type': 'iframe',
            'iframeUrl': 'https://example.com/game',
            'addedAt': datetime.now().strftime('%Y-%m-%d'),
            'tags': ['休闲', '测试']
        }
    ]
    
    # 生成TypeScript代码
    games_code = ""
    for game in test_games:
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
    type: '{game['type']}',"""
        
        if game['type'] == 'iframe':
            games_code += f"\n    iframeUrl: '{game['iframeUrl']}',"
        else:
            games_code += f"\n    staticPath: '{game.get('staticPath', '')}',"
        
        games_code += f"""
    addedAt: '{game['addedAt']}',
    tags: {json.dumps(game['tags'], ensure_ascii=False)}
  }},
"""
    
    print("生成的TypeScript代码:")
    print(games_code)
    print("语法测试通过！")

if __name__ == '__main__':
    test_game_data_generation() 