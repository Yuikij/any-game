export interface Game {
  id: string;
  title: string;
  description?: string;
  category: string;
  categoryId: string;
  thumbnail: string;
  path: string;
  featured?: boolean;
  type: 'iframe' | 'static';
  iframeUrl?: string;
  staticPath?: string;
  addedAt: string;
  tags?: string[];
}

export interface Category {
  id: string;
  name: string;
  description?: string;
  count: number;
  slug: string;
} 