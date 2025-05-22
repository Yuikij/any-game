import Link from 'next/link';
import { Category } from '@/types';

interface CategoryCardProps {
  category: Category;
}

export default function CategoryCard({ category }: CategoryCardProps) {
  return (
    <Link 
      href={`/categories/${category.id}`}
      className="bg-white p-4 rounded-lg shadow text-center hover:shadow-md transition-shadow"
    >
      <h3 className="font-bold mb-1">{category.name}</h3>
      <p className="text-sm text-gray-600">{category.count} 款游戏</p>
    </Link>
  );
} 