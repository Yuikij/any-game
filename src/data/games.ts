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
    title: 'Forever Gold',
    description: '一款有趣的休闲游戏',
    category: '休闲',
    categoryId: '1',
    thumbnail: '/games/thumbnails/default.jpg',
    path: '/games/1',
    featured: false,
    type: 'iframe',
    iframeUrl: 'https://html-classic.itch.zone/html/13725449/play/index.html',
    addedAt: '2025-05-23',
    tags: ["休闲"]
  },
  {
    id: '2',
    title: 'Arcane Earth - Increment Clicker',
    description: '一款有趣的休闲游戏',
    category: '休闲',
    categoryId: '1',
    thumbnail: '/games/thumbnails/default.jpg',
    path: '/games/2',
    featured: false,
    type: 'iframe',
    iframeUrl: 'https://html-classic.itch.zone/html/13744329/ArcaneEarth/index.html',
    addedAt: '2025-05-23',
    tags: ["休闲"]
  },
  {
    id: '3',
    title: 'Lucky Dig',
    description: '一款有趣的模拟游戏',
    category: '模拟',
    categoryId: '1',
    thumbnail: '/games/thumbnails/default.jpg',
    path: '/games/3',
    featured: false,
    type: 'iframe',
    iframeUrl: 'https://html-classic.itch.zone/html/13694006/_dig_game_html/index.html',
    addedAt: '2025-05-23',
    tags: ["模拟"]
  },
  {
    id: '4',
    title: 'Sort the Court!',
    description: '一款有趣的模拟游戏',
    category: '模拟',
    categoryId: '1',
    thumbnail: '/games/thumbnails/default.jpg',
    path: '/games/4',
    featured: false,
    type: 'iframe',
    iframeUrl: 'https://html-classic.itch.zone/html/347310/index.html?v=1542780889',
    addedAt: '2025-05-23',
    tags: ["模拟"]
  },
  {
    id: '5',
    title: 'Batter Up!',
    description: '一款有趣的动作游戏',
    category: '动作',
    categoryId: '3',
    thumbnail: '/games/thumbnails/default.jpg',
    path: '/games/5',
    featured: false,
    type: 'iframe',
    iframeUrl: 'https://html-classic.itch.zone/html/11461904/index.html',
    addedAt: '2025-05-23',
    tags: ["动作"]
  },
  {
    id: '6',
    title: 'We Become What We Behold',
    description: '一款有趣的休闲游戏',
    category: '休闲',
    categoryId: '1',
    thumbnail: '/games/thumbnails/default.jpg',
    path: '/games/6',
    featured: false,
    type: 'iframe',
    iframeUrl: 'https://html-classic.itch.zone/html/300364/index.html?v=1542781840',
    addedAt: '2025-05-23',
    tags: ["休闲"]
  },
  {
    id: '7',
    title: 'RetroFab',
    description: '一款有趣的模拟游戏',
    category: '模拟',
    categoryId: '1',
    thumbnail: '/games/thumbnails/default.jpg',
    path: '/games/7',
    featured: false,
    type: 'iframe',
    iframeUrl: 'https://html-classic.itch.zone/html/5770112/index.html?v=1732313714',
    addedAt: '2025-05-23',
    tags: ["模拟", "复古"]
  },
  {
    id: '8',
    title: 'Categories',
    description: '一款有趣的休闲游戏',
    category: '休闲',
    categoryId: '1',
    thumbnail: '/games/thumbnails/default.jpg',
    path: '/games/8',
    featured: false,
    type: 'static',
    staticPath: 'https://armorgames.com/category/player-level-games',
    addedAt: '2025-05-23',
    tags: ["休闲"]
  },
  {
    id: '1',
    title: 'Forever Gold',
    description: '一款有趣的休闲游戏',
    category: '休闲',
    categoryId: '1',
    thumbnail: '/games/thumbnails/default.jpg',
    path: '/games/1',
    featured: false,
    type: 'iframe',
    iframeUrl: 'https://html-classic.itch.zone/html/13725449/play/index.html',
    addedAt: '2025-05-23',
    tags: ["休闲"]
  },
  {
    id: '2',
    title: 'Arcane Earth - Increment Clicker',
    description: '一款有趣的休闲游戏',
    category: '休闲',
    categoryId: '1',
    thumbnail: '/games/thumbnails/default.jpg',
    path: '/games/2',
    featured: false,
    type: 'iframe',
    iframeUrl: 'https://html-classic.itch.zone/html/13744329/ArcaneEarth/index.html',
    addedAt: '2025-05-23',
    tags: ["休闲"]
  },
  {
    id: '3',
    title: 'Lucky Dig',
    description: '一款有趣的模拟游戏',
    category: '模拟',
    categoryId: '1',
    thumbnail: '/games/thumbnails/default.jpg',
    path: '/games/3',
    featured: false,
    type: 'iframe',
    iframeUrl: 'https://html-classic.itch.zone/html/13694006/_dig_game_html/index.html',
    addedAt: '2025-05-23',
    tags: ["模拟"]
  },
  {
    id: '4',
    title: 'Sort the Court!',
    description: '一款有趣的模拟游戏',
    category: '模拟',
    categoryId: '1',
    thumbnail: '/games/thumbnails/default.jpg',
    path: '/games/4',
    featured: false,
    type: 'iframe',
    iframeUrl: 'https://html-classic.itch.zone/html/347310/index.html?v=1542780889',
    addedAt: '2025-05-23',
    tags: ["模拟"]
  },
  {
    id: '5',
    title: 'Batter Up!',
    description: '一款有趣的动作游戏',
    category: '动作',
    categoryId: '3',
    thumbnail: '/games/thumbnails/default.jpg',
    path: '/games/5',
    featured: false,
    type: 'iframe',
    iframeUrl: 'https://html-classic.itch.zone/html/11461904/index.html',
    addedAt: '2025-05-23',
    tags: ["动作"]
  },
  {
    id: '6',
    title: 'We Become What We Behold',
    description: '一款有趣的休闲游戏',
    category: '休闲',
    categoryId: '1',
    thumbnail: '/games/thumbnails/default.jpg',
    path: '/games/6',
    featured: false,
    type: 'iframe',
    iframeUrl: 'https://html-classic.itch.zone/html/300364/index.html?v=1542781840',
    addedAt: '2025-05-23',
    tags: ["休闲"]
  },
  {
    id: '7',
    title: 'RetroFab',
    description: '一款有趣的模拟游戏',
    category: '模拟',
    categoryId: '1',
    thumbnail: '/games/thumbnails/default.jpg',
    path: '/games/7',
    featured: false,
    type: 'iframe',
    iframeUrl: 'https://html-classic.itch.zone/html/5770112/index.html?v=1732313714',
    addedAt: '2025-05-23',
    tags: ["模拟", "复古"]
  },
  {
    id: '8',
    title: 'Categories',
    description: '一款有趣的休闲游戏',
    category: '休闲',
    categoryId: '1',
    thumbnail: '/games/thumbnails/default.jpg',
    path: '/games/8',
    featured: false,
    type: 'static',
    staticPath: 'https://armorgames.com/category/player-level-games',
    addedAt: '2025-05-23',
    tags: ["休闲"]
  },
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
