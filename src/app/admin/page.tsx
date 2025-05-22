import { Metadata } from 'next';
import Link from 'next/link';
import { games, categories } from '@/data/games';

export const metadata: Metadata = {
  title: '管理员面板 - AnyGame',
  description: '管理AnyGame平台上的游戏和分类。',
};

export default function AdminPage() {
  return (
    <div className="max-w-6xl mx-auto space-y-8">
      <div className="mb-8">
        <h1 className="text-3xl font-bold mb-4">管理员面板</h1>
        <p className="text-gray-600">
          管理AnyGame平台上的游戏和分类。
        </p>
      </div>
      
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="bg-white p-6 rounded-lg shadow-md">
          <h2 className="text-xl font-bold mb-4">游戏管理</h2>
          
          <div className="flex flex-col space-y-2">
            <Link 
              href="/admin/add-game" 
              className="inline-flex items-center text-blue-600 hover:text-blue-800"
            >
              <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5 mr-2" viewBox="0 0 20 20" fill="currentColor">
                <path fillRule="evenodd" d="M10 5a1 1 0 011 1v3h3a1 1 0 110 2h-3v3a1 1 0 11-2 0v-3H6a1 1 0 110-2h3V6a1 1 0 011-1z" clipRule="evenodd" />
              </svg>
              添加新游戏
            </Link>
            
            <Link 
              href="/admin/games" 
              className="inline-flex items-center text-blue-600 hover:text-blue-800"
            >
              <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5 mr-2" viewBox="0 0 20 20" fill="currentColor">
                <path fillRule="evenodd" d="M10 2a8 8 0 100 16 8 8 0 000-16zm0 14a6 6 0 110-12 6 6 0 010 12z" clipRule="evenodd" />
                <path d="M10 4a1 1 0 00-1 1v4a1 1 0 001 1h3a1 1 0 100-2h-2V5a1 1 0 00-1-1z" />
              </svg>
              查看所有游戏
            </Link>
          </div>
          
          <div className="mt-4 p-4 bg-gray-50 rounded">
            <h3 className="font-medium mb-2">统计信息</h3>
            <p className="text-sm">总游戏数: <strong>{games.length}</strong></p>
            <p className="text-sm">精选游戏: <strong>{games.filter(game => game.featured).length}</strong></p>
            <p className="text-sm">最近添加: <strong>{games.slice().sort((a, b) => new Date(b.addedAt).getTime() - new Date(a.addedAt).getTime())[0]?.title || '无'}</strong></p>
          </div>
        </div>
        
        <div className="bg-white p-6 rounded-lg shadow-md">
          <h2 className="text-xl font-bold mb-4">分类管理</h2>
          
          <div className="flex flex-col space-y-2">
            <Link 
              href="/admin/add-category" 
              className="inline-flex items-center text-blue-600 hover:text-blue-800"
            >
              <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5 mr-2" viewBox="0 0 20 20" fill="currentColor">
                <path fillRule="evenodd" d="M10 5a1 1 0 011 1v3h3a1 1 0 110 2h-3v3a1 1 0 11-2 0v-3H6a1 1 0 110-2h3V6a1 1 0 011-1z" clipRule="evenodd" />
              </svg>
              添加新分类
            </Link>
            
            <Link 
              href="/admin/categories" 
              className="inline-flex items-center text-blue-600 hover:text-blue-800"
            >
              <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5 mr-2" viewBox="0 0 20 20" fill="currentColor">
                <path fillRule="evenodd" d="M10 2a8 8 0 100 16 8 8 0 000-16zm0 14a6 6 0 110-12 6 6 0 010 12z" clipRule="evenodd" />
                <path d="M10 4a1 1 0 00-1 1v4a1 1 0 001 1h3a1 1 0 100-2h-2V5a1 1 0 00-1-1z" />
              </svg>
              查看所有分类
            </Link>
          </div>
          
          <div className="mt-4 p-4 bg-gray-50 rounded">
            <h3 className="font-medium mb-2">统计信息</h3>
            <p className="text-sm">总分类数: <strong>{categories.length}</strong></p>
            <p className="text-sm">游戏最多的分类: <strong>
              {categories.sort((a, b) => b.count - a.count)[0]?.name || '无'}
              ({categories.sort((a, b) => b.count - a.count)[0]?.count || 0}款游戏)
            </strong></p>
          </div>
        </div>
      </div>
      
      <div className="bg-white p-6 rounded-lg shadow-md">
        <h2 className="text-xl font-bold mb-4">管理工具</h2>
        
        <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-4">
          <Link 
            href="/admin/settings" 
            className="p-4 border border-gray-200 rounded hover:bg-gray-50 transition-colors"
          >
            <h3 className="font-medium">网站设置</h3>
            <p className="text-sm text-gray-600 mt-1">管理网站基本设置和SEO信息</p>
          </Link>
          
          <Link 
            href="/admin/users" 
            className="p-4 border border-gray-200 rounded hover:bg-gray-50 transition-colors"
          >
            <h3 className="font-medium">用户管理</h3>
            <p className="text-sm text-gray-600 mt-1">管理网站用户和权限设置</p>
          </Link>
          
          <Link 
            href="/admin/import" 
            className="p-4 border border-gray-200 rounded hover:bg-gray-50 transition-colors"
          >
            <h3 className="font-medium">批量导入</h3>
            <p className="text-sm text-gray-600 mt-1">从其他平台批量导入游戏</p>
          </Link>
        </div>
      </div>
      
      <div className="text-center py-4">
        <Link href="/" className="text-blue-600 hover:underline">
          返回网站首页
        </Link>
      </div>
    </div>
  );
} 