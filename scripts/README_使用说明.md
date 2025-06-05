# 游戏管理器使用说明

## 🚀 功能特性

`game_manager.py` 是一个集成了所有功能的游戏数据管理工具：

- ✅ **智能爬虫**：支持多个游戏平台，自动检测CSS选择器
- ✅ **自动缩略图生成**：找不到缩略图时自动生成美观的预览图
- ✅ **增强iframe验证**：严格过滤无效URL，支持白名单和智能评分
- ✅ **代理支持**：全局代理设置，支持科学上网
- ✅ **API搜索**：SerpAPI和Google Custom Search API支持
- ✅ **数据清理**：去重、验证、修复等功能

## 📦 安装依赖

```bash
cd scripts
pip install -r requirements.txt
```

## 🔧 配置

### 方法1：直接修改代码（推荐）
编辑 `game_manager.py` 文件中的 `Config` 类：

```python
class Config:
    # 代理配置
    USE_PROXY = True         # 启用代理
    PROXY_HOST = '127.0.0.1' # 代理地址
    PROXY_PORT = '7890'      # 代理端口
    
    # 白名单配置
    STRICT_WHITELIST = False # 智能模式（推荐）
    
    # API配置（可选）
    SERPAPI_KEY = "your_serpapi_key"
    GOOGLE_API_KEY = "your_google_api_key"
    GOOGLE_CX = "your_custom_search_engine_id"
```

### 方法2：环境变量
```bash
export USE_PROXY=true
export PROXY_HOST=127.0.0.1
export PROXY_PORT=7890
export STRICT_WHITELIST=false
export SERPAPI_KEY=your_key
```

### 方法3：命令行参数
```bash
python game_manager.py --use-proxy --strict-whitelist
```

## 🎮 支持的游戏网站

- **itch.io** - HTML5游戏平台
- **GameJolt** - 独立游戏社区
- **CrazyGames** - 在线游戏平台（包含新游戏）
- **GameDistribution** - HTML5游戏分发平台
- **Scratch MIT** - 创意编程平台
- **Miniplay** - 热门游戏平台

## 📋 使用方法

### 查看当前配置
```bash
python game_manager.py --show-config
```

### 全面管理（推荐）
```bash
python game_manager.py --action all --max-games 20
```

### 只爬取新游戏
```bash
python game_manager.py --action crawl --max-games 10
```

### 只清理数据
```bash
python game_manager.py --action clean
```

### 只修复缩略图
```bash
python game_manager.py --action fix-thumbnails
```

## 🎨 缩略图功能

- 自动检测是否已有专属缩略图
- 找不到时自动生成美观的渐变或几何图案缩略图
- 支持多种颜色主题和样式
- 自动添加游戏标题文字和装饰元素

## 🛡️ 安全特性

### 智能URL验证
- 严格过滤无效和恶意URL
- 基于域名、路径、文件名的评分系统
- 排除广告、追踪、社交媒体等非游戏内容

### 双重验证模式
1. **严格白名单模式**：只接受预定义的可信域名
2. **智能验证模式**：白名单优先 + AI评分系统（推荐）

## 🚦 反爬虫策略

- 智能延迟：根据不同平台调整请求频率
- 随机请求头：模拟真实浏览器访问
- 429错误处理：自动增加延迟避免封IP
- 特殊平台处理：针对不同网站的优化策略

## 📊 日志和监控

运行时会生成 `game_manager.log` 文件，包含：
- 爬取进度和结果
- 错误信息和警告
- URL验证详情
- 缩略图生成状态

## ❓ 常见问题

**Q: 代理不生效怎么办？**
A: 检查代理服务器是否运行，端口是否正确。可以用 `--show-config` 查看配置状态。

**Q: 缩略图生成失败？**
A: 确保安装了 Pillow 库：`pip install Pillow>=10.0.0`

**Q: 爬取速度太慢？**
A: 可以调整配置中的延迟设置，但不建议设置过快避免被封IP。

**Q: 想添加新的游戏网站？**
A: 在 `PREMIUM_GAME_SITES` 和 `EMBEDDABLE_DOMAINS` 中添加相应配置即可。 