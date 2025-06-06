import { Game, Category } from '../types';

export const categories: Category[] = [
  { id: '1', name: '休闲', description: '简单有趣的休闲游戏，适合所有年龄段玩家', count: 7, slug: 'casual' },
  { id: '2', name: '益智', description: '锻炼大脑的益智游戏，提升思维能力', count: 0, slug: 'puzzle' },
  { id: '3', name: '动作', description: '刺激的动作游戏，考验你的反应速度', count: 0, slug: 'action' },
  { id: '4', name: '卡牌', description: '卡牌和棋牌类游戏，策略与运气的结合', count: 0, slug: 'card' },
  { id: '5', name: '体育', description: '各类体育模拟游戏，感受体育竞技的乐趣', count: 0, slug: 'sports' },
  { id: '6', name: '棋盘', description: '经典的棋盘游戏，考验战略思维', count: 0, slug: 'board' },
];

export const games: Game[] = [
  {
    id: 'basic_itch.io_html5_1749135019_0',
    title: 'SIDE EFFECTS',
    description: '来自itch.io HTML5的HTML5游戏',
    category: '休闲',
    categoryId: '1',
    thumbnail: '/games/thumbnails/default.jpg',
    path: '/games/basic_itch.io_html5_1749135019_0',
    featured: false,
    type: 'iframe',
    iframeUrl: 'https://itch.io/games/html5',
    addedAt: '2025-06-05',
    tags: ["HTML5", "在线", "itch.io HTML5"]
  },
  {
    id: 'basic_itch.io_html5_1749135085_4',
    title: 'Sort the Court!',
    description: '来自itch.io HTML5的HTML5游戏',
    category: '休闲',
    categoryId: '1',
    thumbnail: '/games/thumbnails/default.jpg',
    path: '/games/basic_itch.io_html5_1749135085_4',
    featured: false,
    type: 'iframe',
    iframeUrl: 'https://html-classic.itch.zone/html/347310/index.html?v=1542780889',
    addedAt: '2025-06-05',
    tags: ["HTML5", "在线", "itch.io HTML5"]
  },
  {
    id: 'basic_itch.io_html5_1749135133_7',
    title: 'We Become What We Behold',
    description: '来自itch.io HTML5的HTML5游戏',
    category: '休闲',
    categoryId: '1',
    thumbnail: '/games/thumbnails/default.jpg',
    path: '/games/basic_itch.io_html5_1749135133_7',
    featured: false,
    type: 'iframe',
    iframeUrl: 'https://html-classic.itch.zone/html/300364/index.html?v=1542781840',
    addedAt: '2025-06-05',
    tags: ["HTML5", "在线", "itch.io HTML5"]
  },
  {
    id: 'basic_itch.io_html5_1749135601_10',
    title: 'Exhibit of Sorrows',
    description: '来自itch.io HTML5的HTML5游戏',
    category: '休闲',
    categoryId: '1',
    thumbnail: '/games/thumbnails/default.jpg',
    path: '/games/basic_itch.io_html5_1749135601_10',
    featured: false,
    type: 'iframe',
    iframeUrl: 'https://html-classic.itch.zone/html/12276338/index.html',
    addedAt: '2025-06-05',
    tags: ["HTML5", "在线", "itch.io HTML5"]
  },
  {
    id: 'basic_itch.io_html5_1749135855_23',
    title: 'Cattle Crisis',
    description: '来自itch.io HTML5的HTML5游戏',
    category: '休闲',
    categoryId: '1',
    thumbnail: '/games/thumbnails/default.jpg',
    path: '/games/basic_itch.io_html5_1749135855_23',
    featured: false,
    type: 'iframe',
    iframeUrl: 'https://html-classic.itch.zone/html/13903143/index.html',
    addedAt: '2025-06-05',
    tags: ["HTML5", "在线", "itch.io HTML5"]
  },
  {
    id: 'basic_itch.io_html5_1749135975_29',
    title: 'Adventures With Anxiety!',
    description: '来自itch.io HTML5的HTML5游戏',
    category: '休闲',
    categoryId: '1',
    thumbnail: '/games/thumbnails/default.jpg',
    path: '/games/basic_itch.io_html5_1749135975_29',
    featured: false,
    type: 'iframe',
    iframeUrl: 'https://html-classic.itch.zone/html/1830885/index.html?v=1577643761',
    addedAt: '2025-06-05',
    tags: ["HTML5", "在线", "itch.io HTML5"]
  },
  {
    id: 'basic_itch.io_html5_1749136063_34',
    title: 'Evolution',
    description: '来自itch.io HTML5的HTML5游戏',
    category: '休闲',
    categoryId: '1',
    thumbnail: '/games/thumbnails/default.jpg',
    path: '/games/basic_itch.io_html5_1749136063_34',
    featured: false,
    type: 'iframe',
    iframeUrl: 'https://html-classic.itch.zone/html/438808-627293/Evolution/index.html?v=1732313819',
    addedAt: '2025-06-05',
    tags: ["HTML5", "在线", "itch.io HTML5"]
  },
];

export const getFeaturedGames = (): Game[] => {
  return games.filter(game => game.featured);
};

export const getRecentGames = (limit: number = 8): Game[] => {
  return games
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
