import { NextRequest, NextResponse } from 'next/server';
// import { addGame } from '@/lib/addGame';
// import { Game } from '@/types';

// 配置为Edge Runtime以支持Cloudflare Pages
export const runtime = 'edge';

// eslint-disable-next-line @typescript-eslint/no-unused-vars
export async function POST(_request: NextRequest) {
  try {
    // 在Edge Runtime环境下，文件系统操作不被支持
    // 这个功能只在开发环境或Node.js Runtime中可用
    return NextResponse.json({ 
      success: false, 
      message: '游戏添加功能在生产环境中不可用。请使用Python脚本 (scripts/game_manager.py) 在构建时添加游戏。'
    }, { status: 501 });
    
    /*
    // 原有的游戏添加逻辑，仅在Node.js Runtime中可用
    const data = await request.json();
    
    // 从表单数据中提取游戏信息
    const gameData: Omit<Game, 'id' | 'path' | 'addedAt'> = {
      title: data.title,
      description: data.description,
      category: '', // 将从categoryId查询获取
      categoryId: data.categoryId,
      thumbnail: data.thumbnail,
      featured: data.featured === 'on' || data.featured === true,
      type: data.type,
      tags: data.tags ? data.tags.split(',').map((tag: string) => tag.trim()) : [],
    };
    
    // 根据类型添加不同的URL
    if (data.type === 'iframe') {
      gameData.iframeUrl = data.iframeUrl;
    } else if (data.type === 'static') {
      gameData.staticPath = data.staticPath;
    }
    
    // 查找分类名称
    const categoryName = data.categoryName;
    if (categoryName) {
      gameData.category = categoryName;
    }
    
    // 添加游戏
    const result = await addGame(gameData);
    
    if (result.success) {
      return NextResponse.json({ 
        success: true, 
        message: result.message,
        id: result.id
      });
    } else {
      return NextResponse.json({ 
        success: false, 
        message: result.message 
      }, { status: 400 });
    }
    */
  } catch (error) {
    console.error('添加游戏API错误:', error);
    return NextResponse.json({ 
      success: false, 
      message: `服务器错误: ${error instanceof Error ? error.message : String(error)}` 
    }, { status: 500 });
  }
}

// 处理从网站爬取游戏的请求
// eslint-disable-next-line @typescript-eslint/no-unused-vars
export async function PUT(_request: NextRequest) {
  try {
    // 在Edge Runtime环境下，不支持复杂的爬取操作
    return NextResponse.json({ 
      success: false, 
      message: '游戏爬取功能在生产环境中不可用。请使用Python脚本 (scripts/game_manager.py) 在构建时爬取和添加游戏。'
    }, { status: 501 });
    
    /*
    // 原有的爬取逻辑，仅在Node.js Runtime中可用
    const data = await request.json();
    const url = data.url;
    
    if (!url) {
      return NextResponse.json({ 
        success: false, 
        message: '请提供游戏网站URL'
      }, { status: 400 });
    }
    
    // 这里实现爬取逻辑，目前只返回未实现的消息
    return NextResponse.json({ 
      success: false, 
      message: '游戏爬取功能尚未实现，请手动添加游戏'
    });
    */
  } catch (error) {
    console.error('爬取游戏API错误:', error);
    return NextResponse.json({ 
      success: false, 
      message: `服务器错误: ${error instanceof Error ? error.message : String(error)}` 
    }, { status: 500 });
  }
} 