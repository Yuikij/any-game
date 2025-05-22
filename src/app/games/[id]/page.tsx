import { Metadata } from 'next';
import Image from 'next/image';
import Link from 'next/link';
import { notFound } from 'next/navigation';
import { getGameById, getCategoryById } from '@/data/games';

interface GamePageProps {
  params: {
    id: string;
  };
}

export function generateMetadata({ params }: GamePageProps): Metadata {
  const game = getGameById(params.id);
  
  if (!game) {
    return {
      title: '游戏未找到 - AnyGame',
    };
  }
  
  return {
    title: `${game.title} - 免费在线玩 - AnyGame`,
    description: game.description || `在线免费玩${game.title}，无需下载，直接在浏览器中畅玩。`,
    keywords: `${game.title}, ${game.category}, 免费游戏, 在线游戏, ${game.tags?.join(', ')}`,
  };
}

export default function GamePage({ params }: GamePageProps) {
  const game = getGameById(params.id);
  
  if (!game) {
    notFound();
  }
  
  const category = getCategoryById(game.categoryId);
  
  return (
    <div className="space-y-8">
      <div className="flex flex-col md:flex-row gap-8">
        {/* 游戏缩略图 */}
        <div className="md:w-1/3">
          <div className="bg-white p-4 rounded-lg shadow">
            <Image
              src={game.thumbnail}
              alt={game.title}
              width={500}
              height={300}
              className="w-full rounded"
            />
          </div>
        </div>
        
        {/* 游戏信息 */}
        <div className="md:w-2/3">
          <div className="flex items-center gap-2 text-sm text-gray-500 mb-2">
            <Link href="/" className="hover:text-blue-600">
              首页
            </Link>
            <span>&gt;</span>
            {category && (
              <>
                <Link href={`/categories/${category.id}`} className="hover:text-blue-600">
                  {category.name}
                </Link>
                <span>&gt;</span>
              </>
            )}
            <span>{game.title}</span>
          </div>
          
          <h1 className="text-3xl font-bold mb-4">{game.title}</h1>
          
          {game.description && (
            <p className="text-gray-600 mb-4">{game.description}</p>
          )}
          
          <div className="flex flex-wrap gap-2 mb-6">
            <span className="category-badge">{game.category}</span>
            {game.tags?.map(tag => (
              <span key={tag} className="inline-block px-2 py-1 text-xs rounded-full bg-gray-100 text-gray-700">
                {tag}
              </span>
            ))}
          </div>
          
          <a 
            href={game.type === 'iframe' ? game.iframeUrl : game.staticPath} 
            target="_blank"
            rel="noopener noreferrer"
            className="btn-primary inline-block"
          >
            立即游玩
          </a>
        </div>
      </div>
      
      {/* 游戏内容 */}
      <div className="bg-white p-6 rounded-lg shadow-md">
        <h2 className="text-xl font-bold mb-4">游戏介绍</h2>
        
        {game.type === 'iframe' ? (
          <div className="aspect-video w-full">
            <iframe 
              src={game.iframeUrl} 
              className="w-full h-full border-0 rounded"
              allowFullScreen
              loading="lazy"
              title={game.title}
            ></iframe>
          </div>
        ) : (
          <div className="aspect-video w-full bg-gray-100 flex items-center justify-center rounded">
            <Link 
              href={game.staticPath || '#'} 
              className="btn-primary"
              target="_blank"
            >
              在新窗口中打开游戏
            </Link>
          </div>
        )}
        
        <div className="mt-6 space-y-4">
          <p>
            {game.description || `${game.title}是一款非常有趣的${game.category}游戏，你可以直接在浏览器中免费游玩，无需下载任何应用程序。`}
          </p>
          <p>
            如果你喜欢这款游戏，不要忘了查看我们的其他{game.category}游戏！
          </p>
        </div>
      </div>
    </div>
  );
} 