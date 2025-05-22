import { Game } from '@/types';
import { games, categories } from '@/data/games';
import fs from 'fs';
import path from 'path';

/**
 * 添加新游戏到数据库
 * @param game 新游戏数据
 * @returns 添加是否成功
 */
export async function addGame(game: Omit<Game, 'id' | 'path' | 'addedAt'>): Promise<{success: boolean; message: string; id?: string}> {
  try {
    // 验证游戏数据
    if (!game.title) {
      return { success: false, message: '游戏标题不能为空' };
    }
    
    if (!game.category || !game.categoryId) {
      return { success: false, message: '游戏分类不能为空' };
    }
    
    if (!categories.find(c => c.id === game.categoryId)) {
      return { success: false, message: '无效的分类ID' };
    }
    
    if (!game.thumbnail) {
      return { success: false, message: '游戏缩略图不能为空' };
    }
    
    if (game.type === 'iframe' && !game.iframeUrl) {
      return { success: false, message: 'iframe类型的游戏必须提供iframeUrl' };
    }
    
    if (game.type === 'static' && !game.staticPath) {
      return { success: false, message: 'static类型的游戏必须提供staticPath' };
    }
    
    // 生成新ID
    const newId = (Math.max(...games.map(g => parseInt(g.id)), 0) + 1).toString();
    
    // 创建游戏路径
    const gamePath = `/games/${game.title.toLowerCase().replace(/\s+/g, '-')}`;
    
    // 添加新游戏
    const newGame: Game = {
      id: newId,
      path: gamePath,
      addedAt: new Date().toISOString().split('T')[0],
      ...game
    };
    
    // 读取当前数据
    const gamesFilePath = path.join(process.cwd(), 'src/data/games.ts');
    const content = fs.readFileSync(gamesFilePath, 'utf8');
    
    // 解析现有数组
    const gamesArrayStart = content.indexOf('export const games: Game[] = [');
    const gamesArrayEnd = content.indexOf('];', gamesArrayStart);
    
    if (gamesArrayStart === -1 || gamesArrayEnd === -1) {
      return { success: false, message: '无法在文件中找到游戏数组' };
    }
    
    // 添加新游戏到数组
    const gameString = `  {
    id: '${newGame.id}',
    title: '${newGame.title}',
    description: '${newGame.description || ''}',
    category: '${newGame.category}',
    categoryId: '${newGame.categoryId}',
    thumbnail: '${newGame.thumbnail}',
    path: '${newGame.path}',
    featured: ${newGame.featured || false},
    type: '${newGame.type}',
    ${newGame.type === 'iframe' ? `iframeUrl: '${newGame.iframeUrl}'` : `staticPath: '${newGame.staticPath}'`},
    addedAt: '${newGame.addedAt}',
    tags: [${newGame.tags ? newGame.tags.map(tag => `'${tag}'`).join(', ') : ''}]
  },`;
    
    // 插入新游戏
    const updatedContent = 
      content.substring(0, gamesArrayEnd) + 
      '\n' + gameString + 
      content.substring(gamesArrayEnd);
    
    // 写入文件
    fs.writeFileSync(gamesFilePath, updatedContent, 'utf8');
    
    return { 
      success: true, 
      message: `成功添加游戏：${newGame.title}`,
      id: newGame.id
    };
  } catch (error) {
    console.error('添加游戏时出错:', error);
    return { 
      success: false, 
      message: `添加游戏时出错: ${error instanceof Error ? error.message : String(error)}`
    };
  }
}

/**
 * 从网站爬取游戏信息并添加到数据库
 * @param url 游戏网站URL
 * @returns 添加是否成功
 */
export async function scrapeAndAddGame(url: string): Promise<{success: boolean; message: string; id?: string}> {
  try {
    // 这里只是一个示例函数，实际实现需要根据目标网站的结构编写爬虫逻辑
    // 1. 爬取游戏网页
    // 2. 解析游戏信息
    // 3. 下载游戏缩略图
    // 4. 处理游戏文件
    // 5. 调用addGame函数添加游戏
    
    // 示例实现（模拟爬取结果）
    return { 
      success: false, 
      message: '游戏爬取功能尚未实现，请手动添加游戏'
    };
  } catch (error) {
    console.error('爬取游戏时出错:', error);
    return { 
      success: false, 
      message: `爬取游戏时出错: ${error instanceof Error ? error.message : String(error)}`
    };
  }
} 