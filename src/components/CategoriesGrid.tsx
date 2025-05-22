import { Category } from '@/types';
import CategoryCard from './CategoryCard';

interface CategoriesGridProps {
  categories: Category[];
  columns?: 2 | 3 | 4 | 6;
}

export default function CategoriesGrid({ 
  categories, 
  columns = 6 
}: CategoriesGridProps) {
  let gridClass = 'grid grid-cols-2 gap-4';
  
  switch (columns) {
    case 2:
      gridClass = 'grid grid-cols-1 sm:grid-cols-2 gap-4';
      break;
    case 3:
      gridClass = 'grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-4';
      break;
    case 4:
      gridClass = 'grid grid-cols-2 sm:grid-cols-2 md:grid-cols-4 gap-4';
      break;
    case 6:
      gridClass = 'grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4';
      break;
  }

  return (
    <div className={gridClass}>
      {categories.map(category => (
        <CategoryCard key={category.id} category={category} />
      ))}
    </div>
  );
} 