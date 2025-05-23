# 游戏爬虫和文件修复工具

这个目录包含了用于爬取游戏数据和修复数据文件格式的脚本。

## 文件说明

### 核心脚本
- `advanced_crawler.py` - **🚀 高级爬虫**，优先下载HTML5游戏到本地，支持API搜索
- `strict_clean_games.py` - **严格清理脚本**，只保留真正可iframe嵌入的游戏
- `remove_duplicates.py` - **去重脚本**，移除重复的游戏

### 辅助脚本
- `enhanced_crawler.py` - 增强版爬虫，专门收集可iframe嵌入的游戏
- `game_crawler.py` - 标准爬虫脚本
- `fix_games_file.py` - 修复games.ts文件格式的脚本
- `clean_games.py` - 清理脚本，移除无效的游戏对象
- `merge_games.py` - 合并增强版爬虫结果到games.ts文件
- `rebuild_games_file.py` - 重建games.ts文件脚本
- `crawl_and_fix.py` - 组合脚本，自动运行爬虫并修复文件格式

### 配置文件
- `install_dependencies.py` - 安装依赖包的脚本
- `requirements.txt` - 依赖包列表
- `api_config_example.txt` - API配置示例

## 使用方法

### 1. 安装依赖

首先安装所需的依赖包：

```bash
python install_dependencies.py
```

或者直接使用pip安装：

```bash
pip install -r requirements.txt
```

### 2. 🚀 推荐：使用高级爬虫

高级爬虫是最新的解决方案，具有以下特点：
- ✅ **优先下载HTML5游戏到本地**
- ✅ **支持API搜索扩展**
- ✅ **自动解压ZIP游戏包**
- ✅ **智能识别主HTML文件**
- ✅ **备选iframe嵌入方案**

```bash
python advanced_crawler.py
```

#### 配置API（可选）

如果想要更好的搜索效果，可以配置API：

1. 复制 `api_config_example.txt` 为 `.env`
2. 填入真实的API密钥：
   - **SerpAPI**: 注册 https://serpapi.com/
   - **Google Custom Search**: 获取 https://developers.google.com/custom-search/v1/introduction

```bash
# 设置环境变量（Windows）
set SERPAPI_KEY=your_actual_key
set GOOGLE_API_KEY=your_actual_key
set GOOGLE_CX=your_actual_cx

# 设置环境变量（Linux/Mac）
export SERPAPI_KEY=your_actual_key
export GOOGLE_API_KEY=your_actual_key
export GOOGLE_CX=your_actual_cx

# 然后运行高级爬虫
python advanced_crawler.py
```

### 3. 严格清理现有数据

如果发现games.ts文件中有跳转到外部链接的游戏，使用严格清理脚本：

```bash
python strict_clean_games.py
```

### 4. 移除重复游戏

```bash
python remove_duplicates.py
```

### 5. 其他爬虫选项

#### 增强版爬虫（专门收集iframe游戏）

```bash
python enhanced_crawler.py
python merge_games.py
```

#### 标准爬虫

```bash
python game_crawler.py
```

## 游戏类型优先级

### 1. 本地HTML5游戏（最优）
- 游戏文件下载到 `public/games/` 目录
- 完全本地运行，无需网络连接
- 加载速度最快，用户体验最佳
- 支持ZIP包自动解压

### 2. iframe嵌入游戏（备选）
- 使用可信任的嵌入域名
- 在平台内运行，不跳转外链
- 需要网络连接

### 3. 外部链接（不推荐）
- 会被严格清理脚本过滤掉
- 用户体验差，容易流失

## 推荐工作流程

### 🎯 最佳实践流程

```bash
# 1. 运行高级爬虫（优先本地下载）
python advanced_crawler.py

# 2. 严格清理确保质量
python strict_clean_games.py

# 3. 移除重复游戏
python remove_duplicates.py

# 4. 如需更多iframe游戏，运行增强版爬虫
python enhanced_crawler.py
python merge_games.py

# 5. 再次去重
python remove_duplicates.py
```

### 解决外部链接跳转问题

如果发现游戏点击后跳转到外部链接：

```bash
# 1. 严格清理，只保留真正可嵌入的游戏
python strict_clean_games.py

# 2. 移除重复游戏
python remove_duplicates.py

# 3. 使用高级爬虫补充本地游戏
python advanced_crawler.py
```

## 高级爬虫特性

### 智能下载功能
- 🔍 **自动识别下载链接**：HTML文件、ZIP包、游戏资源
- 📦 **ZIP包处理**：自动解压并找到主HTML文件
- 🎯 **智能文件选择**：优先选择 index.html、game.html 等主文件
- 📏 **文件大小限制**：避免下载过大文件（50MB限制）

### API搜索增强
- 🔍 **SerpAPI集成**：使用Google搜索API扩展搜索范围
- 🌐 **Google Custom Search**：自定义搜索引擎支持
- 🔄 **多源搜索**：结合多个API获得更好结果

### 质量保证
- ✅ **严格验证**：确保下载的是真正的游戏文件
- 🚫 **黑名单过滤**：自动过滤无效域名和链接
- 🎮 **游戏类型检测**：区分本地游戏和iframe游戏

## 当前状态

经过严格清理后，当前games.ts文件包含：
- **7个真正可嵌入的游戏**
- **所有游戏都使用`html-classic.itch.zone`域名**
- **确保不会跳转到外部链接**
- **所有游戏都可以在平台内直接运行**

### 当前游戏列表
1. Forever Gold - 休闲游戏
2. Arcane Earth - Increment Clicker - 休闲游戏
3. Lucky Dig - 模拟游戏
4. Sort the Court! - 模拟游戏
5. Batter Up! - 动作游戏
6. We Become What We Behold - 休闲游戏
7. RetroFab - 模拟游戏

## 数据验证机制

### 过滤的无效内容
- ❌ 公司介绍和网站标语
- ❌ YouTube视频链接
- ❌ 网站首页和分类页
- ❌ 广告和跟踪链接
- ❌ 标题过短或过长的内容
- ❌ 新闻文章和收购消息
- ❌ 跳转到外部链接的游戏

### 保留的有效内容
- ✅ 真正的游戏名称和描述
- ✅ 可下载的HTML5游戏文件
- ✅ 可嵌入的iframe游戏
- ✅ 通过白名单验证的域名

## 自定义配置

### 高级爬虫配置

可以在`advanced_crawler.py`文件中修改：

- `PREMIUM_GAME_SITES` - 高质量游戏平台配置
- `EMBEDDABLE_DOMAINS` - 可嵌入的域名白名单
- `LOCAL_GAMES_DIR` - 本地游戏存储目录

### API配置

- `SERPAPI_KEY` - SerpAPI密钥
- `GOOGLE_API_KEY` - Google API密钥
- `GOOGLE_CX` - Google自定义搜索引擎ID

## 注意事项

1. **优先级策略**：
   - 本地HTML5游戏 > iframe嵌入 > 外部链接
   - 自动选择最佳方案

2. **文件管理**：
   - 本地游戏存储在 `public/games/` 目录
   - 自动创建游戏子目录
   - 支持ZIP包自动解压

3. **API使用**：
   - API配置是可选的
   - 不配置API仍然可以正常工作
   - API可以显著提升搜索效果

4. **备份机制**：
   - 所有修改前都会自动备份
   - 备份文件保存为 `.backup` 后缀

## 日志文件

- `advanced_crawler.log` - 高级爬虫日志
- `strict_clean_games.log` - 严格清理日志
- `remove_duplicates.log` - 去重脚本日志
- `enhanced_crawler.log` - 增强版爬虫日志
- `game_crawler.log` - 标准爬虫日志 