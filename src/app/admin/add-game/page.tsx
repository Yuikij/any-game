'use client';

import { useState } from 'react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { categories } from '@/data/games';

export default function AddGamePage() {
  const router = useRouter();
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState<{text: string; type: 'success' | 'error'} | null>(null);
  const [gameType, setGameType] = useState<'iframe' | 'static'>('iframe');
  
  const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    setLoading(true);
    setMessage(null);
    
    const formData = new FormData(e.currentTarget);
    const data = Object.fromEntries(formData.entries());
    
    // 获取选中的分类名称
    const categoryId = data.categoryId as string;
    const category = categories.find(c => c.id === categoryId);
    if (category) {
      data.categoryName = category.name;
    }
    
    try {
      const response = await fetch('/api/games/add', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(data),
      });
      
      const result = await response.json();
      
      if (result.success) {
        setMessage({
          text: result.message,
          type: 'success'
        });
        
        // 清空表单
        e.currentTarget.reset();
        setGameType('iframe');
        
        // 延时跳转到游戏页面
        setTimeout(() => {
          if (result.id) {
            router.push(`/games/${result.id}`);
          }
        }, 2000);
      } else {
        setMessage({
          text: result.message,
          type: 'error'
        });
      }
    } catch (error) {
      setMessage({
        text: `添加游戏时出错: ${error instanceof Error ? error.message : String(error)}`,
        type: 'error'
      });
    } finally {
      setLoading(false);
    }
  };
  
  const handleScrape = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    setLoading(true);
    setMessage(null);
    
    const formData = new FormData(e.currentTarget);
    const url = formData.get('gameUrl');
    
    try {
      const response = await fetch('/api/games/add', {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ url }),
      });
      
      const result = await response.json();
      
      setMessage({
        text: result.message,
        type: result.success ? 'success' : 'error'
      });
      
      if (result.success && result.id) {
        // 清空表单
        e.currentTarget.reset();
        
        // 延时跳转到游戏页面
        setTimeout(() => {
          router.push(`/games/${result.id}`);
        }, 2000);
      }
    } catch (error) {
      setMessage({
        text: `爬取游戏时出错: ${error instanceof Error ? error.message : String(error)}`,
        type: 'error'
      });
    } finally {
      setLoading(false);
    }
  };
  
  return (
    <div className="max-w-4xl mx-auto space-y-8">
      <div className="mb-8">
        <Link href="/admin" className="text-blue-600 hover:underline mb-4 inline-block">
          &larr; 返回管理面板
        </Link>
        <h1 className="text-3xl font-bold mb-4">添加新游戏</h1>
        <p className="text-gray-600">
          使用此表单将新游戏添加到AnyGame平台。支持iframe和静态HTML游戏。
        </p>
      </div>
      
      {message && (
        <div className={`p-4 rounded-md ${message.type === 'success' ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'}`}>
          {message.text}
        </div>
      )}
      
      <form className="bg-white p-6 rounded-lg shadow-md space-y-6" onSubmit={handleSubmit}>
        <div className="space-y-4">
          <h2 className="text-xl font-bold">基本信息</h2>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label htmlFor="title" className="block text-sm font-medium text-gray-700 mb-1">
                游戏标题 *
              </label>
              <input
                type="text"
                id="title"
                name="title"
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                required
              />
            </div>
            
            <div>
              <label htmlFor="category" className="block text-sm font-medium text-gray-700 mb-1">
                游戏分类 *
              </label>
              <select
                id="category"
                name="categoryId"
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                required
              >
                <option value="">选择分类</option>
                {categories.map(category => (
                  <option key={category.id} value={category.id}>
                    {category.name}
                  </option>
                ))}
              </select>
            </div>
          </div>
          
          <div>
            <label htmlFor="description" className="block text-sm font-medium text-gray-700 mb-1">
              游戏描述
            </label>
            <textarea
              id="description"
              name="description"
              rows={3}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            ></textarea>
          </div>
          
          <div>
            <label htmlFor="tags" className="block text-sm font-medium text-gray-700 mb-1">
              标签（用逗号分隔）
            </label>
            <input
              type="text"
              id="tags"
              name="tags"
              placeholder="例如：休闲,益智,策略"
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>
          
          <div>
            <label htmlFor="thumbnail" className="block text-sm font-medium text-gray-700 mb-1">
              缩略图路径 *
            </label>
            <input
              type="text"
              id="thumbnail"
              name="thumbnail"
              placeholder="/games/thumbnails/your-game.jpg"
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              required
            />
            <p className="text-xs text-gray-500 mt-1">
              请先上传缩略图到 /public/games/thumbnails/ 目录
            </p>
          </div>
          
          <div className="flex items-center">
            <input
              type="checkbox"
              id="featured"
              name="featured"
              className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
            />
            <label htmlFor="featured" className="ml-2 block text-sm text-gray-700">
              设为精选游戏
            </label>
          </div>
        </div>
        
        <div className="space-y-4 border-t pt-4">
          <h2 className="text-xl font-bold">游戏类型</h2>
          
          <div className="space-y-4">
            <div className="flex items-center">
              <input
                type="radio"
                id="type-iframe"
                name="type"
                value="iframe"
                className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300"
                checked={gameType === 'iframe'}
                onChange={() => setGameType('iframe')}
              />
              <label htmlFor="type-iframe" className="ml-2 block text-sm text-gray-700">
                iframe嵌入
              </label>
            </div>
            
            <div className="ml-6" style={{ display: gameType === 'iframe' ? 'block' : 'none' }}>
              <label htmlFor="iframeUrl" className="block text-sm font-medium text-gray-700 mb-1">
                iframe URL
              </label>
              <input
                type="text"
                id="iframeUrl"
                name="iframeUrl"
                placeholder="https://example.com/game"
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                required={gameType === 'iframe'}
              />
            </div>
            
            <div className="flex items-center">
              <input
                type="radio"
                id="type-static"
                name="type"
                value="static"
                className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300"
                checked={gameType === 'static'}
                onChange={() => setGameType('static')}
              />
              <label htmlFor="type-static" className="ml-2 block text-sm text-gray-700">
                静态HTML文件
              </label>
            </div>
            
            <div className="ml-6" style={{ display: gameType === 'static' ? 'block' : 'none' }}>
              <label htmlFor="staticPath" className="block text-sm font-medium text-gray-700 mb-1">
                静态文件路径
              </label>
              <input
                type="text"
                id="staticPath"
                name="staticPath"
                placeholder="/games/your-game/index.html"
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                required={gameType === 'static'}
              />
              <p className="text-xs text-gray-500 mt-1">
                请先上传游戏文件到 /public/games/[游戏名]/ 目录
              </p>
            </div>
          </div>
        </div>
        
        <div className="pt-4 border-t">
          <button
            type="submit"
            className="btn-primary"
            disabled={loading}
          >
            {loading ? '添加中...' : '添加游戏'}
          </button>
        </div>
      </form>
      
      <div className="bg-white p-6 rounded-lg shadow-md">
        <h2 className="text-xl font-bold mb-4">从网站爬取游戏</h2>
        <p className="text-gray-600 mb-4">
          输入游戏网站URL，系统将尝试抓取游戏信息并自动添加。
        </p>
        
        <form className="space-y-4" onSubmit={handleScrape}>
          <div>
            <label htmlFor="gameUrl" className="block text-sm font-medium text-gray-700 mb-1">
              游戏网站URL
            </label>
            <input
              type="url"
              id="gameUrl"
              name="gameUrl"
              placeholder="https://example.com/game-page"
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              required
            />
          </div>
          
          <button
            type="submit"
            className="bg-green-600 hover:bg-green-700 text-white px-4 py-2 rounded font-medium transition-colors"
            disabled={loading}
          >
            {loading ? '爬取中...' : '爬取并添加'}
          </button>
        </form>
      </div>
    </div>
  );
} 