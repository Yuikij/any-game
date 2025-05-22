import Link from 'next/link';
import GameGrid from '@/components/GameGrid';
import CategoriesGrid from '@/components/CategoriesGrid';
import { getFeaturedGames, getRecentGames, categories } from '@/data/games';

export default function Home() {
  const featuredGames = getFeaturedGames();
  const recentGames = getRecentGames(8);

  return (
    <div className="space-y-12">
      {/* 英雄区域 */}
      <section className="relative h-80 bg-gradient-to-r from-blue-600 to-purple-600 rounded-xl overflow-hidden">
        <div className="absolute inset-0 bg-black/30 z-10"></div>
        <div className="relative z-20 h-full flex flex-col justify-center items-center text-white text-center px-4">
          <h1 className="text-4xl font-bold mb-4">超过 1000+ 免费游戏</h1>
          <p className="text-xl mb-6">直接在浏览器中畅玩，无需下载</p>
          <Link href="/categories" className="btn-primary">
            浏览所有游戏
          </Link>
        </div>
      </section>

      {/* 特色游戏 */}
      <section>
        <div className="flex justify-between items-center mb-6">
          <h2 className="text-2xl font-bold">特色游戏</h2>
          <Link href="/featured" className="text-blue-600 hover:underline">
            查看全部
          </Link>
        </div>
        <GameGrid games={featuredGames} columns={3} featured={true} />
      </section>

      {/* 最近添加 */}
      <section>
        <div className="flex justify-between items-center mb-6">
          <h2 className="text-2xl font-bold">最近添加</h2>
          <Link href="/recent" className="text-blue-600 hover:underline">
            查看全部
          </Link>
        </div>
        <GameGrid games={recentGames} columns={4} />
      </section>

      {/* 游戏分类 */}
      <section>
        <h2 className="text-2xl font-bold mb-6">游戏分类</h2>
        <CategoriesGrid categories={categories} columns={6} />
      </section>
    </div>
  );
}
