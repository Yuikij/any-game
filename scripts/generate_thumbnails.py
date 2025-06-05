#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
缩略图生成工具 - 为游戏生成美观的预览图
功能：
1. 生成彩色渐变背景的缩略图
2. 添加游戏标题文字
3. 批量生成多种样式
"""

import os
from PIL import Image, ImageDraw, ImageFont
import random
import math
import colorsys

# 项目配置
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
THUMBNAILS_DIR = os.path.join(PROJECT_ROOT, 'public', 'games', 'thumbnails')

# 确保目录存在
os.makedirs(THUMBNAILS_DIR, exist_ok=True)

def generate_gradient_background(width, height, color1, color2):
    """生成渐变背景"""
    image = Image.new('RGB', (width, height))
    
    for y in range(height):
        # 计算渐变比例
        ratio = y / height
        
        # 线性插值
        r = int(color1[0] * (1 - ratio) + color2[0] * ratio)
        g = int(color1[1] * (1 - ratio) + color2[1] * ratio)
        b = int(color1[2] * (1 - ratio) + color2[2] * ratio)
        
        # 填充这一行
        for x in range(width):
            image.putpixel((x, y), (r, g, b))
    
    return image

def generate_geometric_pattern(width, height, base_color):
    """生成几何图案背景"""
    image = Image.new('RGB', (width, height), base_color)
    draw = ImageDraw.Draw(image)
    
    # 随机几何图案
    patterns = ['circles', 'triangles', 'rectangles', 'lines']
    pattern = random.choice(patterns)
    
    # 生成亮色和暗色变体
    r, g, b = base_color
    light_color = (min(255, r + 40), min(255, g + 40), min(255, b + 40))
    dark_color = (max(0, r - 40), max(0, g - 40), max(0, b - 40))
    
    if pattern == 'circles':
        for _ in range(8):
            x = random.randint(0, width)
            y = random.randint(0, height)
            radius = random.randint(20, 60)
            color = random.choice([light_color, dark_color])
            draw.ellipse([x-radius, y-radius, x+radius, y+radius], 
                        fill=color, outline=None)
    
    elif pattern == 'triangles':
        for _ in range(6):
            points = []
            for _ in range(3):
                points.append((random.randint(0, width), random.randint(0, height)))
            color = random.choice([light_color, dark_color])
            draw.polygon(points, fill=color)
    
    elif pattern == 'rectangles':
        for _ in range(10):
            x1 = random.randint(0, width//2)
            y1 = random.randint(0, height//2)
            x2 = x1 + random.randint(30, 80)
            y2 = y1 + random.randint(20, 60)
            color = random.choice([light_color, dark_color])
            draw.rectangle([x1, y1, x2, y2], fill=color)
    
    elif pattern == 'lines':
        for _ in range(15):
            x1 = random.randint(0, width)
            y1 = random.randint(0, height)
            x2 = random.randint(0, width)
            y2 = random.randint(0, height)
            color = random.choice([light_color, dark_color])
            draw.line([x1, y1, x2, y2], fill=color, width=random.randint(2, 8))
    
    return image

def get_contrast_color(bg_color):
    """根据背景色获取对比色文字"""
    r, g, b = bg_color
    # 计算亮度
    brightness = (r * 299 + g * 587 + b * 114) / 1000
    
    if brightness > 128:
        return (0, 0, 0)  # 深色文字
    else:
        return (255, 255, 255)  # 浅色文字

def create_game_thumbnail(title, style='gradient', width=300, height=200):
    """创建游戏缩略图"""
    
    # 预定义的颜色主题
    color_themes = [
        # 蓝色主题
        {'primary': (52, 152, 219), 'secondary': (155, 89, 182)},
        # 绿色主题
        {'primary': (46, 204, 113), 'secondary': (52, 152, 219)},
        # 橙色主题
        {'primary': (230, 126, 34), 'secondary': (231, 76, 60)},
        # 紫色主题
        {'primary': (155, 89, 182), 'secondary': (52, 73, 94)},
        # 红色主题
        {'primary': (231, 76, 60), 'secondary': (192, 57, 43)},
        # 青色主题
        {'primary': (26, 188, 156), 'secondary': (22, 160, 133)},
        # 黄色主题
        {'primary': (241, 196, 15), 'secondary': (230, 126, 34)},
        # 灰色主题
        {'primary': (52, 73, 94), 'secondary': (44, 62, 80)},
    ]
    
    theme = random.choice(color_themes)
    
    if style == 'gradient':
        # 渐变背景
        image = generate_gradient_background(width, height, theme['primary'], theme['secondary'])
    else:
        # 几何图案背景
        image = generate_geometric_pattern(width, height, theme['primary'])
    
    draw = ImageDraw.Draw(image)
    
    # 尝试加载字体
    try:
        # Windows系统字体
        font_large = ImageFont.truetype("arial.ttf", 24)
        font_small = ImageFont.truetype("arial.ttf", 16)
    except:
        try:
            # Linux系统字体
            font_large = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 24)
            font_small = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 16)
        except:
            # 默认字体
            font_large = ImageFont.load_default()
            font_small = ImageFont.load_default()
    
    # 添加半透明覆盖层
    overlay = Image.new('RGBA', (width, height), (0, 0, 0, 80))
    image = Image.alpha_composite(image.convert('RGBA'), overlay).convert('RGB')
    draw = ImageDraw.Draw(image)
    
    # 处理标题文字
    if len(title) > 20:
        title = title[:17] + "..."
    
    # 获取文字颜色
    text_color = (255, 255, 255)  # 白色文字在深色覆盖层上
    
    # 计算文字位置（居中）
    bbox = draw.textbbox((0, 0), title, font=font_large)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    
    text_x = (width - text_width) // 2
    text_y = (height - text_height) // 2
    
    # 添加文字阴影
    shadow_offset = 2
    draw.text((text_x + shadow_offset, text_y + shadow_offset), title, 
             fill=(0, 0, 0), font=font_large)
    
    # 添加主文字
    draw.text((text_x, text_y), title, fill=text_color, font=font_large)
    
    # 添加装饰元素
    if random.choice([True, False]):
        # 添加小图标或装饰
        icon_size = 20
        icon_x = width - icon_size - 10
        icon_y = 10
        
        # 简单的游戏手柄图标
        draw.ellipse([icon_x, icon_y, icon_x + icon_size, icon_y + icon_size], 
                    fill=text_color, outline=None)
        draw.ellipse([icon_x + 4, icon_y + 4, icon_x + icon_size - 4, icon_y + icon_size - 4], 
                    fill=theme['primary'], outline=None)
    
    return image

def generate_batch_thumbnails(count=50):
    """批量生成缩略图"""
    print(f"🎨 开始生成 {count} 个游戏缩略图...")
    
    # 游戏标题示例
    game_titles = [
        "Super Adventure", "Puzzle Master", "Racing Fever", "Space Battle",
        "Magic Quest", "Brain Teaser", "Action Hero", "Card Legends",
        "Sport Champion", "Strategy War", "Casual Fun", "Arcade Classic",
        "Pixel Runner", "Tower Defense", "Match Three", "Flying High",
        "Ocean Explorer", "Mountain Climb", "City Builder", "Farm Life",
        "Robot Wars", "Fantasy World", "Ninja Strike", "Pirate Gold",
        "Zombie Escape", "Time Travel", "Crystal Quest", "Dragon Fight",
        "Candy Crush", "Bubble Pop", "Word Search", "Number Game",
        "Color Match", "Shape Shift", "Quick Draw", "Memory Test",
        "Logic Puzzle", "Hidden Object", "Escape Room", "Treasure Hunt",
        "Speed Race", "Jump High", "Fly Far", "Dig Deep",
        "Build Tower", "Save World", "Find Key", "Unlock Door"
    ]
    
    generated_count = 0
    
    for i in range(count):
        try:
            # 随机选择标题和样式
            title = random.choice(game_titles)
            style = random.choice(['gradient', 'geometric'])
            
            # 生成缩略图
            thumbnail = create_game_thumbnail(title, style)
            
            # 生成文件名
            filename = f"auto_game_{i+1:03d}.jpg"
            filepath = os.path.join(THUMBNAILS_DIR, filename)
            
            # 保存图片
            thumbnail.save(filepath, 'JPEG', quality=90, optimize=True)
            
            generated_count += 1
            
            if (i + 1) % 10 == 0:
                print(f"✅ 已生成 {i + 1} 个缩略图...")
        
        except Exception as e:
            print(f"❌ 生成第 {i+1} 个缩略图失败: {e}")
            continue
    
    print(f"🎉 成功生成 {generated_count} 个缩略图！")
    print(f"📁 保存位置: {THUMBNAILS_DIR}")

def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description='游戏缩略图生成工具')
    parser.add_argument('--count', type=int, default=50, help='生成缩略图数量')
    parser.add_argument('--title', type=str, help='生成单个缩略图的标题')
    parser.add_argument('--style', choices=['gradient', 'geometric'], 
                       default='gradient', help='缩略图样式')
    
    args = parser.parse_args()
    
    if args.title:
        # 生成单个缩略图
        print(f"🎨 为 '{args.title}' 生成缩略图...")
        thumbnail = create_game_thumbnail(args.title, args.style)
        filename = f"custom_{args.title.replace(' ', '_').lower()}.jpg"
        filepath = os.path.join(THUMBNAILS_DIR, filename)
        thumbnail.save(filepath, 'JPEG', quality=90, optimize=True)
        print(f"✅ 生成完成: {filename}")
    else:
        # 批量生成
        generate_batch_thumbnails(args.count)

if __name__ == '__main__':
    main() 