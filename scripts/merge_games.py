#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
合并游戏数据脚本
将增强版爬虫的结果合并到games.ts文件中
"""

import os
import json
import logging
from datetime import datetime

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('merge_games.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# 项目配置
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GAMES_DATA_FILE = os.path.join(PROJECT_ROOT, 'src', 'data', 'games.ts')
ENHANCED_GAMES_FILE = os.path.join(PROJECT_ROOT, 'scripts', 'enhanced_games.json')
BACKUP_FILE = os.path.join(PROJECT_ROOT, 'src', 'data', 'games.ts.bak')

def load_enhanced_games():
    """加载增强版爬虫的游戏数据"""
    try:
        if not os.path.exists(ENHANCED_GAMES_FILE):
            logger.error(f"增强版游戏数据文件不存在: {ENHANCED_GAMES_FILE}")
            return []
        
        with open(ENHANCED_GAMES_FILE, 'r', encoding='utf-8') as f:
            games = json.load(f)
        
        logger.info(f"成功加载 {len(games)} 个增强版游戏数据")
        return games
        
    except Exception as e:
        logger.error(f"加载增强版游戏数据失败: {e}")
        return []

def backup_games_file():
    """备份现有的games.ts文件"""
    try:
        if os.path.exists(GAMES_DATA_FILE):
            with open(GAMES_DATA_FILE, 'r', encoding='utf-8') as f:
                content = f.read()
            
            with open(BACKUP_FILE, 'w', encoding='utf-8') as f:
                f.write(content)
            
            logger.info(f"已备份games.ts文件到: {BACKUP_FILE}")
            return True
    except Exception as e:
        logger.error(f"备份文件失败: {e}")
        return False

def generate_game_ts_code(games):
    """生成游戏的TypeScript代码"""
    games_code = ""
    
    for game in games:
        # 转义字符串中的单引号
        title = game['title'].replace("'", "\\'")
        description = game['description'].replace("'", "\\'")
        
        games_code += f"""  {{
    id: '{game['id']}',
    title: '{title}',
    description: '{description}',
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
    
    return games_code

def merge_games():
    """合并游戏数据到games.ts文件"""
    try:
        # 1. 备份现有文件
        if not backup_games_file():
            return False
        
        # 2. 加载增强版游戏数据
        enhanced_games = load_enhanced_games()
        if not enhanced_games:
            logger.warning("没有找到增强版游戏数据")
            return False
        
        # 3. 读取现有的games.ts文件
        if os.path.exists(GAMES_DATA_FILE):
            with open(GAMES_DATA_FILE, 'r', encoding='utf-8') as f:
                content = f.read()
        else:
            content = ""
        
        # 4. 生成新游戏的TypeScript代码
        new_games_code = generate_game_ts_code(enhanced_games)
        
        # 5. 合并到现有文件
        if content and 'export const games: Game[] = [' in content:
            # 找到游戏数组结束的位置
            array_end_pos = content.find('];', content.find('export const games: Game[] = ['))
            if array_end_pos != -1:
                # 在数组结束前插入新游戏
                new_content = content[:array_end_pos] + new_games_code + content[array_end_pos:]
            else:
                logger.error("无法找到游戏数组结束位置")
                return False
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
        
        # 6. 保存文件
        with open(GAMES_DATA_FILE, 'w', encoding='utf-8') as f:
            f.write(new_content)
        
        logger.info(f"✅ 成功合并 {len(enhanced_games)} 个游戏到 {GAMES_DATA_FILE}")
        return True
        
    except Exception as e:
        logger.error(f"合并游戏数据失败: {e}")
        return False

def main():
    """主函数"""
    logger.info("🔄 开始合并增强版游戏数据...")
    
    success = merge_games()
    
    if success:
        logger.info("✅ 游戏数据合并完成！")
        logger.info("💡 提示：所有新添加的游戏都是可以直接在平台内运行的iframe游戏")
    else:
        logger.error("❌ 游戏数据合并失败")

if __name__ == '__main__':
    main() 