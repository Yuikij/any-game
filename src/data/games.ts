import { Game, Category } from '../types';

export const categories: Category[] = [
  { id: '1', name: '休闲', description: '简单有趣的休闲游戏，适合所有年龄段玩家', count: 125, slug: 'casual' },
  { id: '2', name: '益智', description: '锻炼大脑的益智游戏，提升思维能力', count: 98, slug: 'puzzle' },
  { id: '3', name: '动作', description: '刺激的动作游戏，考验你的反应速度', count: 84, slug: 'action' },
  { id: '4', name: '卡牌', description: '卡牌和棋牌类游戏，策略与运气的结合', count: 52, slug: 'card' },
  { id: '5', name: '体育', description: '各类体育模拟游戏，感受体育竞技的乐趣', count: 43, slug: 'sports' },
  { id: '6', name: '棋盘', description: '经典的棋盘游戏，考验战略思维', count: 38, slug: 'board' },
];

export const games: Game[] = [
  {
    id: '1',
    title: '2048',
    description: '移动方块，合并相同的数字，尝试得到2048！',
    category: '益智',
    categoryId: '2',
    thumbnail: '/games/thumbnails/2048.jpg',
    path: '/games/2048',
    featured: true,
    type: 'static',
    staticPath: '/games/2048/index.html',
    addedAt: '2023-05-15',
    tags: ['数字', '益智', '策略']
  },
  {
    id: '2',
    title: '贪吃蛇',
    description: '控制蛇吃食物并成长，但不要撞到墙壁或自己的身体！',
    category: '休闲',
    categoryId: '1',
    thumbnail: '/games/thumbnails/snake.jpg',
    path: '/games/snake',
    featured: true,
    type: 'static',
    staticPath: '/games/snake/index.html',
    addedAt: '2023-06-20',
    tags: ['经典', '休闲']
  },
  {
    id: '3',
    title: '俄罗斯方块',
    description: '经典的俄罗斯方块游戏，尽可能堆叠更多的方块获得高分。',
    category: '益智',
    categoryId: '2',
    thumbnail: '/games/thumbnails/tetris.jpg',
    path: '/games/tetris',
    featured: true,
    type: 'static',
    staticPath: '/games/tetris/index.html',
    addedAt: '2023-04-10',
    tags: ['经典', '益智', '方块']
  },
  {
    id: '4',
    title: '跳跃忍者',
    description: '控制忍者角色跳跃并避开障碍物，看你能跑多远！',
    category: '动作',
    categoryId: '3',
    thumbnail: '/games/thumbnails/ninja.jpg',
    path: '/games/ninja',
    type: 'iframe',
    iframeUrl: 'https://www.example-game.com/ninja-jump',
    addedAt: '2023-07-05',
    tags: ['动作', '跑酷']
  },
  {
    id: '5',
    title: '水果忍者',
    description: '用手指切水果，小心炸弹！',
    category: '休闲',
    categoryId: '1',
    thumbnail: '/games/thumbnails/fruit-ninja.jpg',
    path: '/games/fruit-ninja',
    type: 'iframe',
    iframeUrl: 'https://www.example-game.com/fruit-ninja',
    addedAt: '2023-08-15',
    tags: ['休闲', '切水果']
  },
  {
    id: '6',
    title: '纸牌接龙',
    description: '经典的纸牌接龙游戏，考验你的策略和耐心。',
    category: '卡牌',
    categoryId: '4',
    thumbnail: '/games/thumbnails/solitaire.jpg',
    path: '/games/solitaire',
    type: 'static',
    staticPath: '/games/solitaire/index.html',
    addedAt: '2023-09-01',
    tags: ['卡牌', '经典']
  },
  {
    id: '7',
    title: '象棋',
    description: '传统中国象棋游戏，与电脑对战或邀请朋友一起玩。',
    category: '棋盘',
    categoryId: '6',
    thumbnail: '/games/thumbnails/chess.jpg',
    path: '/games/chess',
    type: 'static',
    staticPath: '/games/chess/index.html',
    addedAt: '2023-10-10',
    tags: ['棋盘', '策略', '传统']
  },
  {
    id: '8',
    title: '飞镖',
    description: '测试你的准确性，瞄准飞镖靶获得高分！',
    category: '体育',
    categoryId: '5',
    thumbnail: '/games/thumbnails/darts.jpg',
    path: '/games/darts',
    type: 'iframe',
    iframeUrl: 'https://www.example-game.com/darts',
    addedAt: '2023-11-05',
    tags: ['体育', '投掷']
  },
  {
    id: '9',
    title: '填字游戏',
    description: '经典填字游戏，挑战你的词汇量！',
    category: '益智',
    categoryId: '2',
    thumbnail: '/games/thumbnails/crossword.jpg',
    path: '/games/crossword',
    type: 'static',
    staticPath: '/games/crossword/index.html',
    addedAt: '2023-12-15',
    tags: ['词汇', '益智']
  }
];

// 辅助函数
export const getFeaturedGames = (): Game[] => {
  return games.filter(game => game.featured);
};

export const getRecentGames = (limit: number = 8): Game[] => {
  return [...games]
    .sort((a, b) => new Date(b.addedAt).getTime() - new Date(a.addedAt).getTime())
    .slice(0, limit);
};

export const getGamesByCategory = (categoryId: string): Game[] => {
  return games.filter(game => game.categoryId === categoryId);
};

export const getGameById = (id: string): Game | undefined => {
  return games.find(game => game.id === id);
};

export const getCategoryById = (id: string): Category | undefined => {
  return categories.find(category => category.id === id);
}; 