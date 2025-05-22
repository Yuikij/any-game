import { Metadata } from 'next';
import GameGrid from '@/components/GameGrid';
import { games } from '@/data/games';

export const metadata: Metadata = {
  title: '热门游戏 - AnyGame',
  description: '发现AnyGame平台上最受欢迎的游戏，这些是玩家们最喜欢的游戏。',
  keywords: '热门游戏, 流行游戏, 最受欢迎, 最多人玩',
};

// 模拟热门游戏，实际项目中可能会基于游戏的访问量或点击率来排序
const popularGames = [...games].sort(() => Math.random() - 0.5).slice(0, 12);

export default function PopularGamesPage() {
  return (
    <div className="space-y-8">
      <div className="mb-8">
        <h1 className="text-3xl font-bold mb-4">热门游戏</h1>
        <p className="text-gray-600">
          这些是我们平台上最受欢迎的游戏，由玩家的喜好和游戏质量决定。
        </p>
      </div>
      
      {popularGames.length > 0 ? (
        <GameGrid games={popularGames} columns={4} />
      ) : (
        <div className="text-center py-12 bg-gray-50 rounded-lg">
          <p className="text-gray-500">暂无热门游戏数据</p>
        </div>
      )}
    </div>
  );
} 