#!/usr/bin/env python3
"""检查游戏统计信息"""

import re
import os

def check_game_stats():
    """检查游戏统计信息"""
    games_file = "src/data/games.ts"
    
    if not os.path.exists(games_file):
        print("❌ 游戏数据文件不存在")
        return
    
    with open(games_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 统计游戏数量
    game_count = content.count('id: \'')
    print(f"📊 游戏统计:")
    print(f"🎮 总游戏数量: {game_count}")
    
    # 统计分类
    categories = re.findall(r"name: '([^']+)'.*?count: (\d+)", content)
    print(f"📂 分类统计:")
    total_category_count = 0
    for name, count in categories:
        count_int = int(count)
        total_category_count += count_int
        print(f"  - {name}: {count} 个游戏")
    
    # 统计缩略图
    print(f"🖼️ 缩略图统计:")
    default_count = content.count("'/games/thumbnails/default.jpg'")
    auto_count = content.count("'/games/thumbnails/auto_game_")
    
    # 统计自定义缩略图（非default且非auto_game_）
    custom_thumbnails = [
        "20.jpg", "21.jpg", "22.jpg", "24.jpg", "25.png", 
        "26.jpg", "27.jpg", "28.jpg"
    ]
    custom_count = sum(content.count(f"'/games/thumbnails/{thumb}'") for thumb in custom_thumbnails)
    
    print(f"  - 默认缩略图: {default_count} 个")
    print(f"  - 自动生成缩略图: {auto_count} 个")
    print(f"  - 自定义缩略图: {custom_count} 个")
    print(f"  - 总缩略图: {default_count + auto_count + custom_count} 个")

if __name__ == "__main__":
    check_game_stats() 