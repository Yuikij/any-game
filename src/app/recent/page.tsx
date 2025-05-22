import { Metadata } from 'next';
import GameGrid from '@/components/GameGrid';
import { getRecentGames } from '@/data/games';

export const metadata: Metadata = {
  title: '最近添加的游戏 - AnyGame',
  description: '查看AnyGame平台上最新添加的游戏，保持更新，尝试最新的游戏体验。',
  keywords: '新游戏, 最新游戏, 最近添加, 最新上线',
};

export default function RecentGamesPage() {
  const recentGames = getRecentGames(20); // 获取最近20款游戏
  
  return (
    <div className="space-y-8">
      <div className="mb-8">
        <h1 className="text-3xl font-bold mb-4">最近添加</h1>
        <p className="text-gray-600">
          浏览我们平台上最新添加的游戏，保持更新，尝试最新的游戏体验。
        </p>
      </div>
      
      {recentGames.length > 0 ? (
        <GameGrid games={recentGames} columns={4} />
      ) : (
        <div className="text-center py-12 bg-gray-50 rounded-lg">
          <p className="text-gray-500">暂无最近添加的游戏</p>
        </div>
      )}
    </div>
  );
} 