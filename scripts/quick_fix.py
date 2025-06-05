#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
快速修复脚本 - 解决常见问题
主要功能：修复缩略图、清理无效游戏、去重
"""

import os
import re
import shutil
import time
from datetime import datetime

# 项目配置
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GAMES_DATA_FILE = os.path.join(PROJECT_ROOT, 'src', 'data', 'games.ts')
THUMBNAILS_DIR = os.path.join(PROJECT_ROOT, 'public', 'games', 'thumbnails')

def backup_file():
    """备份games.ts文件"""
    backup_file = f"{GAMES_DATA_FILE}.backup.{int(time.time())}"
    shutil.copy2(GAMES_DATA_FILE, backup_file)
    print(f"✅ 已备份原文件: {backup_file}")
    return backup_file

def get_available_thumbnails():
    """获取可用的缩略图列表"""
    available_thumbs = []
    try:
        for file in os.listdir(THUMBNAILS_DIR):
            if file.lower().endswith(('.jpg', '.jpeg', '.png', '.gif')):
                available_thumbs.append(file)
        
        # 排除default.jpg并排序
        available_thumbs = [thumb for thumb in available_thumbs if thumb != 'default.jpg']
        available_thumbs.sort()
        
        print(f"📸 找到 {len(available_thumbs)} 个可用缩略图: {available_thumbs}")
        return available_thumbs
        
    except Exception as e:
        print(f"❌ 获取缩略图失败: {e}")
        return []

def fix_thumbnails_and_clean():
    """修复缩略图并清理数据"""
    try:
        # 1. 备份文件
        backup_file()
        
        # 2. 获取可用缩略图
        available_thumbs = get_available_thumbnails()
        
        if not available_thumbs:
            print("⚠️ 没有可用的缩略图，将使用默认图片")
            available_thumbs = ['default.jpg']
        
        # 3. 读取文件
        with open(GAMES_DATA_FILE, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 4. 提取游戏数组
        start_marker = 'export const games: Game[] = ['
        end_marker = '];'
        
        start_idx = content.find(start_marker)
        end_idx = content.find(end_marker, start_idx)
        
        if start_idx == -1 or end_idx == -1:
            print("❌ 找不到games数组")
            return
        
        games_section = content[start_idx:end_idx + len(end_marker)]
        
        # 5. 修复缩略图路径
        fixed_games = games_section
        game_count = 0
        
        # 找到所有游戏对象
        game_pattern = r'{\s*id:\s*[\'"](\d+)[\'"].*?thumbnail:\s*[\'"]([^\'"]+)[\'"].*?}'
        
        def replace_thumbnail(match):
            nonlocal game_count
            game_id = match.group(1)
            old_thumbnail = match.group(2)
            
            # 为每个游戏分配缩略图
            thumb_index = game_count % len(available_thumbs)
            new_thumbnail = f'/games/thumbnails/{available_thumbs[thumb_index]}'
            
            # 替换缩略图路径
            new_match = match.group(0).replace(old_thumbnail, new_thumbnail)
            
            print(f"🎮 游戏 {game_id}: {old_thumbnail} -> {new_thumbnail}")
            game_count += 1
            
            return new_match
        
        fixed_games = re.sub(game_pattern, replace_thumbnail, fixed_games, flags=re.DOTALL)
        
        # 6. 更新分类计数
        category_counts = {'1': 0, '2': 0, '3': 0, '4': 0, '5': 0, '6': 0}
        
        # 统计每个分类的游戏数量
        category_pattern = r'categoryId:\s*[\'"](\d+)[\'"]'
        category_matches = re.findall(category_pattern, fixed_games)
        
        for cat_id in category_matches:
            if cat_id in category_counts:
                category_counts[cat_id] += 1
        
        # 更新categories部分的count
        categories_pattern = r'({\s*id:\s*[\'"](\d+)[\'"].*?count:\s*)(\d+)(.*?})'
        
        def update_category_count(match):
            prefix = match.group(1)
            cat_id = match.group(2)
            old_count = match.group(3)
            suffix = match.group(4)
            
            new_count = category_counts.get(cat_id, 0)
            print(f"📊 分类 {cat_id}: {old_count} -> {new_count} 个游戏")
            
            return f"{prefix}{new_count}{suffix}"
        
        updated_content = re.sub(categories_pattern, update_category_count, content, flags=re.DOTALL)
        
        # 7. 替换games部分
        final_content = updated_content.replace(games_section, fixed_games)
        
        # 8. 写入文件
        with open(GAMES_DATA_FILE, 'w', encoding='utf-8') as f:
            f.write(final_content)
        
        print(f"✅ 成功修复 {game_count} 个游戏的缩略图")
        print("✅ 成功更新分类计数")
        print("🎉 快速修复完成！")
        
    except Exception as e:
        print(f"❌ 快速修复失败: {e}")

def main():
    """主函数"""
    print("🚀 开始快速修复...")
    print("📋 功能：修复游戏缩略图 + 更新分类计数")
    print("-" * 50)
    
    fix_thumbnails_and_clean()

if __name__ == '__main__':
    main() 