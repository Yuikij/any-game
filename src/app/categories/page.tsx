import { Metadata } from 'next';
import CategoriesGrid from '@/components/CategoriesGrid';
import { categories } from '@/data/games';

export const metadata: Metadata = {
  title: '游戏分类 - AnyGame',
  description: '浏览各种类型的免费在线游戏，包括休闲、益智、动作、卡牌、体育和棋盘游戏等。',
  keywords: '游戏分类, 免费游戏, 在线游戏, 休闲游戏, 益智游戏',
};

export default function CategoriesPage() {
  return (
    <div className="space-y-8">
      <div className="mb-8">
        <h1 className="text-3xl font-bold mb-4">游戏分类</h1>
        <p className="text-gray-600">
          浏览各种类型的免费在线游戏，找到你最喜欢的游戏类型。
        </p>
      </div>
      
      <CategoriesGrid categories={categories} columns={3} />
    </div>
  );
} 