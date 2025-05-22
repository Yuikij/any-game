# AnyGame - 在线游戏聚合平台

AnyGame是一个使用Next.js和TailwindCSS构建的在线游戏聚合平台，支持各种类型的游戏（iframe嵌入和静态HTML游戏）。这个平台允许用户浏览、搜索和玩游戏，同时提供了管理员界面用于添加和管理游戏内容。

## 特性

- 响应式网页设计，适配各种设备
- 游戏分类系统，便于用户查找游戏
- 支持两种游戏类型：
  - iframe嵌入式游戏（从外部网站嵌入）
  - 静态HTML游戏（本地托管在项目中）
- SEO优化的页面结构
- 模块化架构，便于扩展
- 管理面板用于添加和管理游戏
- 游戏导入工具，支持批量添加游戏

## 技术栈

- [Next.js](https://nextjs.org/) - React框架
- [TailwindCSS](https://tailwindcss.com/) - 样式框架
- [TypeScript](https://www.typescriptlang.org/) - 类型安全
- [React](https://reactjs.org/) - UI库

## 项目结构

```
any-game/
├── public/                  # 静态资源
│   ├── games/              # 游戏资源
│   │   ├── thumbnails/     # 游戏缩略图
│   │   └── [game-name]/    # 静态游戏文件夹
├── src/
│   ├── app/                # 应用页面
│   │   ├── admin/          # 管理员界面
│   │   ├── api/            # API路由
│   │   ├── categories/     # 分类页面
│   │   ├── games/          # 游戏页面
│   │   ├── layout.tsx      # 全局布局
│   │   └── page.tsx        # 首页
│   ├── components/         # UI组件
│   │   ├── GameCard.tsx    # 游戏卡片组件
│   │   ├── GameGrid.tsx    # 游戏网格组件
│   │   ├── CategoryCard.tsx # 分类卡片组件
│   │   └── CategoriesGrid.tsx # 分类网格组件
│   ├── data/               # 数据文件
│   │   └── games.ts        # 游戏和分类数据
│   ├── lib/                # 工具函数
│   │   ├── addGame.ts      # 添加游戏的函数
│   │   └── importGames.ts  # 导入游戏的函数
│   └── types/              # 类型定义
│       └── index.ts        # 游戏和分类类型
```

## 安装

1. 克隆仓库:

```bash
git clone https://github.com/yourusername/any-game.git
cd any-game
```

2. 安装依赖:

```bash
npm install
```

3. 运行开发服务器:

```bash
npm run dev
```

4. 打开浏览器访问 [http://localhost:3000](http://localhost:3000)

## 添加新游戏

### 通过管理界面添加

1. 访问管理面板：[http://localhost:3000/admin](http://localhost:3000/admin)
2. 点击"添加新游戏"
3. 填写游戏信息，包括标题、描述、分类等
4. 上传游戏缩略图到 `public/games/thumbnails/`
5. 根据游戏类型，选择:
   - **iframe嵌入**: 提供游戏的iframe URL
   - **静态HTML**: 上传游戏文件到 `public/games/[游戏名]/`，确保有一个 `index.html` 文件

### 手动添加到数据文件

如果你希望直接编辑数据文件，可以修改 `src/data/games.ts` 文件：

1. 在 `games` 数组中添加新的游戏对象
2. 确保提供所有必要的属性（id, title, category, categoryId, thumbnail, path, type等）

### 批量导入游戏

对于有大量静态HTML游戏需要导入的情况，可以使用导入工具：

1. 将游戏文件放置在 `public/games/[游戏目录]/` 下，每个游戏一个文件夹
2. 确保每个游戏文件夹有一个 `index.html` 文件
3. 在管理面板中使用批量导入功能

## 自定义和扩展

### 添加新分类

修改 `src/data/games.ts` 中的 `categories` 数组，添加新的分类对象。

### 自定义样式

本项目使用TailwindCSS，你可以修改 `tailwind.config.js` 文件来自定义颜色、字体等样式。

### 添加新功能

项目采用模块化架构，你可以轻松添加新功能：

1. 在 `src/components` 中创建新的UI组件
2. 在 `src/app` 中添加新的页面
3. 在 `src/lib` 中添加新的工具函数

## 搜索引擎优化

每个页面都包含适当的元数据，以优化搜索引擎索引：

- 每个游戏页面使用游戏标题和描述
- 分类页面包含分类信息
- 标题、描述和关键词都经过优化

## 许可证

本项目使用 [MIT 许可证](LICENSE)。请注意，虽然平台代码是开源的，但添加到平台的游戏可能有各自的许可限制。
