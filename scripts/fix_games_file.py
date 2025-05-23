#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
修复games.ts文件格式的脚本
将文件开头的游戏数据正确放入games数组中
"""

import os
import re
import json
import logging

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('fix_games_file.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# 项目配置
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GAMES_DATA_FILE = os.path.join(PROJECT_ROOT, 'src', 'data', 'games.ts')
BACKUP_FILE = os.path.join(PROJECT_ROOT, 'src', 'data', 'games.ts.bak')

def fix_games_file():
    """修复games.ts文件格式"""
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
        
        # 2. 创建正确的文件结构
        # 提取import语句
        import_match = re.search(r'import\s+{.*?}\s+from\s+.*?;', original_content, re.DOTALL)
        if not import_match:
            # 如果找不到import语句，创建一个
            import_statement = "import { Game, Category } from '../types';"
        else:
            import_statement = import_match.group(0)
        
        # 提取categories数组
        categories_match = re.search(r'export\s+const\s+categories:\s+Category\[\]\s+=\s+\[(.*?)\];', original_content, re.DOTALL)
        if categories_match:
            categories_content = categories_match.group(1).strip()
        else:
            # 创建默认的categories数组
            categories_content = """
  { id: '1', name: '休闲', description: '简单有趣的休闲游戏，适合所有年龄段玩家', count: 125, slug: 'casual' },
  { id: '2', name: '益智', description: '锻炼大脑的益智游戏，提升思维能力', count: 98, slug: 'puzzle' },
  { id: '3', name: '动作', description: '刺激的动作游戏，考验你的反应速度', count: 84, slug: 'action' },
  { id: '4', name: '卡牌', description: '卡牌和棋牌类游戏，策略与运气的结合', count: 52, slug: 'card' },
  { id: '5', name: '体育', description: '各类体育模拟游戏，感受体育竞技的乐趣', count: 43, slug: 'sports' },
  { id: '6', name: '棋盘', description: '经典的棋盘游戏，考验战略思维', count: 38, slug: 'board' }
"""
        
        # 3. 提取所有游戏对象
        # 使用正则表达式匹配所有游戏对象
        game_pattern = r'{\s*id:\s*\'[^\']*\'.*?(?:tags:\s*\[[^\]]*\]|iframeUrl:\s*\'[^\']*\'|staticPath:\s*\'[^\']*\')\s*}'
        game_matches = re.findall(game_pattern, original_content, re.DOTALL)
        
        # 清理和格式化游戏对象
        games = []
        for match in game_matches:
            # 清理categories数组误插入到游戏对象中的情况
            match = re.sub(r'tags:\s*\[\s*{\s*id:.*?slug:.*?}\s*,', 'tags: [', match, flags=re.DOTALL)
            
            # 确保每个游戏对象以逗号结尾
            if not match.rstrip().endswith(','):
                match += ','
            
            games.append(match.strip())
        
        logger.info(f"从文件中提取到 {len(games)} 个游戏对象")
        
        # 4. 提取辅助函数
        helper_functions_match = re.search(r'// 辅助函数(.*?)$', original_content, re.DOTALL)
        if helper_functions_match:
            helper_functions = helper_functions_match.group(1).strip()
        else:
            # 创建默认的辅助函数
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
  {"\n  ".join(games)}
];

// 辅助函数
{helper_functions}
"""
        
        # 6. 保存修复后的文件
        with open(GAMES_DATA_FILE, 'w', encoding='utf-8') as f:
            f.write(new_content)
        
        logger.info(f"成功修复games.ts文件，整理了 {len(games)} 个游戏对象")
        return True
        
    except Exception as e:
        logger.error(f"修复文件失败: {e}")
        return False

def main():
    """主函数"""
    logger.info("开始修复games.ts文件...")
    success = fix_games_file()
    if success:
        logger.info("修复完成！")
    else:
        logger.error("修复失败，请检查日志")

if __name__ == '__main__':
    main() 