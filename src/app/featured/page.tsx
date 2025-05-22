import { Metadata } from 'next';
import GameGrid from '@/components/GameGrid';
import { getFeaturedGames } from '@/data/games';

export const metadata: Metadata = {
  title: '精选游戏 - AnyGame',
  description: '发现AnyGame平台上的精选游戏，这些是我们精心挑选的最好玩、最受欢迎的游戏。',
  keywords: '精选游戏, 热门游戏, 推荐游戏, 免费游戏',
};

export default function FeaturedGamesPage() {
  const featuredGames = getFeaturedGames();
  
  return (
    <div className="space-y-8">
      <div className="mb-8">
        <h1 className="text-3xl font-bold mb-4">精选游戏</h1>
        <p className="text-gray-600">
          这些是我们精心挑选的最好玩、最受欢迎的游戏。
        </p>
      </div>
      
      {featuredGames.length > 0 ? (
        <GameGrid games={featuredGames} columns={3} featured={true} />
      ) : (
        <div className="text-center py-12 bg-gray-50 rounded-lg">
          <p className="text-gray-500">暂无精选游戏</p>
        </div>
      )}
    </div>
  );
} 