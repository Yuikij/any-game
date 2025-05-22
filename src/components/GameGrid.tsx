import { Game } from '@/types';
import GameCard from './GameCard';

interface GameGridProps {
  games: Game[];
  columns?: 1 | 2 | 3 | 4 | 6;
  featured?: boolean;
}

export default function GameGrid({ 
  games, 
  columns = 3,
  featured = false 
}: GameGridProps) {
  let gridClass = 'grid grid-cols-1 gap-6';
  
  switch (columns) {
    case 1:
      gridClass = 'grid grid-cols-1 gap-6';
      break;
    case 2:
      gridClass = 'grid grid-cols-1 sm:grid-cols-2 gap-6';
      break;
    case 3:
      gridClass = 'grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-6';
      break;
    case 4:
      gridClass = 'grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-6';
      break;
    case 6:
      gridClass = 'grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-6 gap-4';
      break;
  }

  return (
    <div className={gridClass}>
      {games.map(game => (
        <GameCard 
          key={game.id} 
          game={game} 
          featured={featured && game.featured}
        />
      ))}
    </div>
  );
} 