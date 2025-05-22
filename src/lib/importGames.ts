import fs from 'fs';
import path from 'path';
import { addGame } from './addGame';
import { Game } from '@/types';
import { categories } from '@/data/games';

/**
 * 从静态游戏目录导入游戏
 * @param directory 游戏所在的目录，相对于public目录
 * @param categoryId 分类ID
 */
export async function importGamesFromDirectory(
  directory: string, 
  categoryId: string
): Promise<{success: boolean; message: string; imported: number}> {
  try {
    // 验证分类是否存在
    const category = categories.find(c => c.id === categoryId);
    if (!category) {
      return { success: false, message: '无效的分类ID', imported: 0 };
    }
    
    // 获取目录完整路径（相对于public目录）
    const fullPath = path.join(process.cwd(), 'public', directory);
    
    // 检查目录是否存在
    if (!fs.existsSync(fullPath)) {
      return { success: false, message: `目录 ${directory} 不存在`, imported: 0 };
    }
    
    // 读取目录内容
    const gameFolders = fs.readdirSync(fullPath, { withFileTypes: true })
      .filter(dirent => dirent.isDirectory())
      .map(dirent => dirent.name);
    
    if (gameFolders.length === 0) {
      return { success: false, message: '目录中没有找到游戏', imported: 0 };
    }
    
    // 导入每个游戏
    let importedCount = 0;
    const errors: string[] = [];
    
    for (const folder of gameFolders) {
      // 检查是否有index.html文件
      const indexPath = path.join(fullPath, folder, 'index.html');
      if (!fs.existsSync(indexPath)) {
        errors.push(`${folder}: 缺少index.html文件`);
        continue;
      }
      
      // 检查是否有缩略图
      const thumbsDir = path.join(process.cwd(), 'public', 'games', 'thumbnails');
      if (!fs.existsSync(thumbsDir)) {
        fs.mkdirSync(thumbsDir, { recursive: true });
      }
      
      // 尝试找到缩略图
      let thumbnailPath = '';
      const possibleExtensions = ['.jpg', '.jpeg', '.png', '.webp'];
      for (const ext of possibleExtensions) {
        const testPath = path.join(thumbsDir, `${folder}${ext}`);
        if (fs.existsSync(testPath)) {
          thumbnailPath = `/games/thumbnails/${folder}${ext}`;
          break;
        }
      }
      
      // 如果没有找到缩略图，创建一个默认的
      if (!thumbnailPath) {
        thumbnailPath = `/games/thumbnails/${folder}.jpg`;
        // 这里应该有创建默认缩略图的逻辑，但简化起见，我们只记录错误
        errors.push(`${folder}: 缺少缩略图，需要手动添加到 ${thumbnailPath}`);
      }
      
      // 准备游戏数据
      const gameData: Omit<Game, 'id' | 'path' | 'addedAt'> = {
        title: folder.replace(/-/g, ' ').replace(/\b\w/g, l => l.toUpperCase()), // 转换目录名为标题
        category: category.name,
        categoryId: category.id,
        thumbnail: thumbnailPath,
        type: 'static',
        staticPath: `/${directory}/${folder}/index.html`,
        tags: [category.name]
      };
      
      // 添加游戏
      try {
        const result = await addGame(gameData);
        if (result.success) {
          importedCount++;
        } else {
          errors.push(`${folder}: ${result.message}`);
        }
      } catch (error) {
        errors.push(`${folder}: ${error instanceof Error ? error.message : String(error)}`);
      }
    }
    
    // 返回结果
    if (importedCount === 0) {
      return { 
        success: false, 
        message: `没有导入任何游戏。错误: ${errors.join('; ')}`, 
        imported: 0 
      };
    } else if (errors.length > 0) {
      return { 
        success: true, 
        message: `成功导入 ${importedCount} 个游戏，但有 ${errors.length} 个错误: ${errors.join('; ')}`, 
        imported: importedCount 
      };
    } else {
      return { 
        success: true, 
        message: `成功导入 ${importedCount} 个游戏`, 
        imported: importedCount 
      };
    }
  } catch (error) {
    console.error('导入游戏时出错:', error);
    return { 
      success: false, 
      message: `导入游戏时出错: ${error instanceof Error ? error.message : String(error)}`, 
      imported: 0 
    };
  }
} 