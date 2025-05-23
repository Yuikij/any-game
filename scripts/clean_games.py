#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
清理游戏数据脚本
清理games.ts文件中的无效游戏对象
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
        logging.FileHandler('clean_games.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# 项目配置
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GAMES_DATA_FILE = os.path.join(PROJECT_ROOT, 'src', 'data', 'games.ts')
BACKUP_FILE = os.path.join(PROJECT_ROOT, 'src', 'data', 'games.ts.backup')

def validate_game_object(game_text: str) -> bool:
    """验证游戏对象是否有效"""
    try:
        # 提取标题
        title_match = re.search(r"title:\s*['\"]([^'\"]*)['\"]", game_text)
        if not title_match:
            return False
        
        title = title_match.group(1).strip()
        
        # 提取描述
        desc_match = re.search(r"description:\s*['\"]([^'\"]*)['\"]", game_text, re.DOTALL)
        description = desc_match.group(1).strip() if desc_match else ""
        
        # 提取URL（staticPath或iframeUrl）
        url_match = re.search(r"(?:staticPath|iframeUrl):\s*['\"]([^'\"]*)['\"]", game_text)
        game_url = url_match.group(1).strip() if url_match else ""
        
        # 1. 检查标题有效性
        invalid_titles = [
            'unleash the gamer',
            'play games',
            'free games',
            'online games',
            'game portal',
            'gaming platform',
            'entertainment',
            'company',
            'developer',
            'publisher',
            'studio',
            'browse games',
            'all games'
        ]
        
        title_lower = title.lower()
        if any(invalid in title_lower for invalid in invalid_titles):
            logger.info(f"❌ 无效标题: {title}")
            return False
        
        # 2. 检查标题长度
        if len(title) < 3 or len(title) > 100:
            logger.info(f"❌ 标题长度不合适: {title}")
            return False
        
        # 3. 检查是否是公司/网站介绍
        company_keywords = [
            'we develop',
            'we publish',
            'we reach',
            'million players',
            'international',
            'company',
            'entertainment company',
            'game developer',
            'our audience',
            'multiplayer mobile games',
            'digital games and entertainment'
        ]
        
        desc_lower = description.lower()
        if any(keyword in desc_lower for keyword in company_keywords):
            logger.info(f"❌ 公司介绍: {title}")
            return False
        
        # 4. 检查是否是网站首页或分类页
        invalid_url_patterns = [
            '/games$',
            '/games/$',
            'miniclip.com/games$',
            'itch.io/games$',
            'gamejolt.com/games$',
            'newgrounds.com/games$',
            '/browse$',
            '/category$',
            '/tag/$',
            'youtube.com/embed'
        ]
        
        for pattern in invalid_url_patterns:
            if re.search(pattern, game_url, re.IGNORECASE):
                logger.info(f"❌ 网站首页/分类页: {title} -> {game_url}")
                return False
        
        logger.info(f"✅ 有效游戏: {title}")
        return True
        
    except Exception as e:
        logger.error(f"验证游戏对象失败: {e}")
        return False

def clean_games_file():
    """清理games.ts文件"""
    try:
        # 1. 备份原始文件
        if os.path.exists(GAMES_DATA_FILE):
            with open(GAMES_DATA_FILE, 'r', encoding='utf-8') as f:
                original_content = f.read()
            
            with open(BACKUP_FILE, 'w', encoding='utf-8') as f:
                f.write(original_content)
            logger.info(f"已备份原始文件到: {BACKUP_FILE}")
        else:
            logger.error(f"文件不存在: {GAMES_DATA_FILE}")
            return False
        
        # 2. 提取文件结构
        # 提取import语句
        import_match = re.search(r'import\s+{.*?}\s+from\s+.*?;', original_content, re.DOTALL)
        import_statement = import_match.group(0) if import_match else "import { Game, Category } from '../types';"
        
        # 提取categories数组
        categories_match = re.search(r'export\s+const\s+categories:\s+Category\[\]\s+=\s+\[(.*?)\];', original_content, re.DOTALL)
        if categories_match:
            categories_content = categories_match.group(1).strip()
        else:
            categories_content = """
  { id: '1', name: '休闲', description: '简单有趣的休闲游戏，适合所有年龄段玩家', count: 125, slug: 'casual' },
  { id: '2', name: '益智', description: '锻炼大脑的益智游戏，提升思维能力', count: 98, slug: 'puzzle' },
  { id: '3', name: '动作', description: '刺激的动作游戏，考验你的反应速度', count: 84, slug: 'action' },
  { id: '4', name: '卡牌', description: '卡牌和棋牌类游戏，策略与运气的结合', count: 52, slug: 'card' },
  { id: '5', name: '体育', description: '各类体育模拟游戏，感受体育竞技的乐趣', count: 43, slug: 'sports' },
  { id: '6', name: '棋盘', description: '经典的棋盘游戏，考验战略思维', count: 38, slug: 'board' }
"""
        
        # 3. 提取和验证游戏对象
        game_pattern = r'{\s*id:\s*\'[^\']*\'.*?(?:tags:\s*\[[^\]]*\]|iframeUrl:\s*\'[^\']*\'|staticPath:\s*\'[^\']*\')\s*}'
        game_matches = re.findall(game_pattern, original_content, re.DOTALL)
        
        valid_games = []
        invalid_count = 0
        
        for game_match in game_matches:
            if validate_game_object(game_match):
                # 确保游戏对象以逗号结尾
                if not game_match.rstrip().endswith(','):
                    game_match += ','
                valid_games.append(game_match.strip())
            else:
                invalid_count += 1
        
        logger.info(f"总共找到 {len(game_matches)} 个游戏对象")
        logger.info(f"有效游戏: {len(valid_games)} 个")
        logger.info(f"无效游戏: {invalid_count} 个")
        
        # 4. 提取辅助函数
        helper_functions_match = re.search(r'// 辅助函数(.*?)$', original_content, re.DOTALL)
        if helper_functions_match:
            helper_functions = helper_functions_match.group(1).strip()
        else:
            helper_functions = """
export const getFeaturedGames = (): Game[] => {
  return games.filter(game => game.featured);
};

export const getRecentGames = (limit: number = 8): Game[] => {
  return [...games]
    .sort((a, b) => new Date(b.addedAt).getTime() - new Date(a.addedAt).getTime())
    .slice(0, limit);
};

export const getGamesByCategory = (categoryId: string): Game[] => {
  return games.filter(game => game.categoryId === categoryId);
};

export const getGameById = (id: string): Game | undefined => {
  return games.find(game => game.id === id);
};

export const getCategoryById = (id: string): Category | undefined => {
  return categories.find(category => category.id === id);
};
"""
        
        # 5. 构建新的文件内容
        new_content = f"""{import_statement}

export const categories: Category[] = [
{categories_content}
];

export const games: Game[] = [
  {chr(10).join('  ' + game for game in valid_games)}
];

// 辅助函数
{helper_functions}
"""
        
        # 6. 保存清理后的文件
        with open(GAMES_DATA_FILE, 'w', encoding='utf-8') as f:
            f.write(new_content)
        
        logger.info(f"✅ 成功清理games.ts文件")
        logger.info(f"📊 清理结果: 保留 {len(valid_games)} 个有效游戏，移除 {invalid_count} 个无效游戏")
        return True
        
    except Exception as e:
        logger.error(f"清理文件失败: {e}")
        return False

def main():
    """主函数"""
    logger.info("🧹 开始清理games.ts文件...")
    
    success = clean_games_file()
    
    if success:
        logger.info("✅ 文件清理完成！")
        logger.info("💡 提示：已移除所有无效的游戏对象，只保留真正的游戏")
    else:
        logger.error("❌ 文件清理失败")

if __name__ == '__main__':
    main() 