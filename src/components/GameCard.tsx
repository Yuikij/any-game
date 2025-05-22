import Image from 'next/image';
import Link from 'next/link';
import { Game } from '@/types';

interface GameCardProps {
  game: Game;
  featured?: boolean;
}

export default function GameCard({ game, featured = false }: GameCardProps) {
  return (
    <Link href={game.path} className="game-card group">
      <div className="relative">
        <div className="aspect-video bg-gray-200 relative">
          <Image
            src={game.thumbnail}
            alt={game.title}
            className="game-thumbnail"
            width={400}
            height={225}
          />
        </div>
        {featured && (
          <div className="absolute top-2 right-2 bg-yellow-400 text-yellow-900 px-2 py-1 rounded text-xs font-bold">
            精选
          </div>
        )}
      </div>
      <div className="p-4">
        <h3 className={`font-bold ${featured ? 'text-lg' : ''} group-hover:text-blue-600 transition-colors`}>
          {game.title}
        </h3>
        <div className="flex justify-between items-center mt-2">
          <span className="category-badge">{game.category}</span>
          <span className="text-xs text-gray-500">{game.addedAt}</span>
        </div>
        {game.description && (
          <p className="text-sm text-gray-600 mt-2 line-clamp-2">{game.description}</p>
        )}
      </div>
    </Link>
  );
} 