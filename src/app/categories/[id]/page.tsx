import { Metadata } from 'next';
import Link from 'next/link';
import { notFound } from 'next/navigation';
import GameGrid from '@/components/GameGrid';
import { getCategoryById, getGamesByCategory } from '@/data/games';

interface CategoryPageProps {
  params: {
    id: string;
  };
}

export function generateMetadata({ params }: CategoryPageProps): Metadata {
  const category = getCategoryById(params.id);
  
  if (!category) {
    return {
      title: '分类未找到 - AnyGame',
    };
  }
  
  return {
    title: `${category.name}游戏 - AnyGame`,
    description: category.description || `免费玩最好的${category.name}游戏。发现我们收集的全部${category.count}款${category.name}游戏。`,
    keywords: `${category.name}, 免费游戏, 在线游戏, ${category.name}游戏`,
  };
}

export default function CategoryPage({ params }: CategoryPageProps) {
  const category = getCategoryById(params.id);
  
  if (!category) {
    notFound();
  }
  
  const games = getGamesByCategory(params.id);
  
  return (
    <div className="space-y-8">
      <div className="mb-8">
        <div className="flex items-center gap-2 text-sm text-gray-500 mb-2">
          <Link href="/categories" className="hover:text-blue-600">
            所有分类
          </Link>
          <span>&gt;</span>
          <span>{category.name}</span>
        </div>
        
        <h1 className="text-3xl font-bold mb-2">{category.name}游戏</h1>
        {category.description && (
          <p className="text-gray-600">{category.description}</p>
        )}
        <p className="text-sm text-gray-500 mt-2">共 {category.count} 款游戏</p>
      </div>
      
      {games.length > 0 ? (
        <GameGrid games={games} columns={4} />
      ) : (
        <div className="text-center py-12 bg-gray-50 rounded-lg">
          <p className="text-gray-500">该分类下暂无游戏</p>
        </div>
      )}
    </div>
  );
} 