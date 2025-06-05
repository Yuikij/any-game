#!/usr/bin/env python3
"""
游戏缩略图更新脚本
用于将使用默认缩略图的游戏替换为新生成的自动缩略图
"""

import os
import re
import random
from typing import List, Dict, Any

def read_games_file() -> str:
    """读取游戏数据文件"""
    games_file = "src/data/games.ts"
    if not os.path.exists(games_file):
        raise FileNotFoundError(f"游戏数据文件不存在: {games_file}")
    
    with open(games_file, 'r', encoding='utf-8') as f:
        return f.read()

def get_available_thumbnails() -> List[str]:
    """获取可用的自动生成缩略图列表"""
    thumbnails_dir = "public/games/thumbnails"
    thumbnails = []
    
    for file in os.listdir(thumbnails_dir):
        if file.startswith("auto_game_") and file.endswith(".jpg"):
            thumbnails.append(f"/games/thumbnails/{file}")
    
    # 按编号排序
    thumbnails.sort()
    return thumbnails

def update_default_thumbnails(content: str, available_thumbnails: List[str]) -> str:
    """更新使用默认缩略图的游戏"""
    lines = content.split('\n')
    updated_lines = []
    thumbnail_index = 0
    
    for line in lines:
        # 查找使用默认缩略图的行
        if "thumbnail: '/games/thumbnails/default.jpg'" in line:
            if thumbnail_index < len(available_thumbnails):
                # 替换为自动生成的缩略图
                new_thumbnail = available_thumbnails[thumbnail_index]
                updated_line = line.replace(
                    "'/games/thumbnails/default.jpg'", 
                    f"'{new_thumbnail}'"
                )
                updated_lines.append(updated_line)
                thumbnail_index += 1
                print(f"✅ 更新缩略图: {new_thumbnail}")
            else:
                updated_lines.append(line)
        else:
            updated_lines.append(line)
    
    return '\n'.join(updated_lines)

def main():
    """主函数"""
    print("🎨 开始更新游戏缩略图...")
    
    try:
        # 读取游戏数据
        content = read_games_file()
        print(f"📖 已读取游戏数据文件")
        
        # 获取可用缩略图
        available_thumbnails = get_available_thumbnails()
        print(f"🖼️ 找到 {len(available_thumbnails)} 个自动生成的缩略图")
        
        if not available_thumbnails:
            print("⚠️ 没有找到自动生成的缩略图，请先运行缩略图生成脚本")
            return
        
        # 更新缩略图
        updated_content = update_default_thumbnails(content, available_thumbnails)
        
        # 保存更新后的文件
        with open("src/data/games.ts", 'w', encoding='utf-8') as f:
            f.write(updated_content)
        
        print("✅ 缩略图更新完成！")
        print(f"📁 游戏数据已保存到: src/data/games.ts")
        
    except Exception as e:
        print(f"❌ 更新失败: {e}")

if __name__ == "__main__":
    main() 