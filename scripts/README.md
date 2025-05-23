# 游戏爬虫和文件修复工具

这个目录包含了用于爬取游戏数据和修复数据文件格式的脚本。

## 文件说明

- `game_crawler.py` - 主要爬虫脚本，用于从各个游戏网站爬取游戏数据
- `enhanced_crawler.py` - **增强版爬虫**，专门收集可iframe嵌入的游戏
- `strict_clean_games.py` - **严格清理脚本**，只保留真正可iframe嵌入的游戏
- `remove_duplicates.py` - **去重脚本**，移除重复的游戏
- `fix_games_file.py` - 修复games.ts文件格式的脚本
- `clean_games.py` - 清理脚本，移除无效的游戏对象
- `merge_games.py` - 合并增强版爬虫结果到games.ts文件
- `rebuild_games_file.py` - 重建games.ts文件脚本
- `crawl_and_fix.py` - 组合脚本，自动运行爬虫并修复文件格式
- `install_dependencies.py` - 安装依赖包的脚本
- `requirements.txt` - 依赖包列表

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

### 2. 严格清理现有数据（推荐）

如果发现games.ts文件中有跳转到外部链接的游戏，使用严格清理脚本：

```bash
python strict_clean_games.py
```

这个脚本会：
- ✅ 只保留真正可以iframe嵌入的游戏
- ✅ 移除所有跳转到外部链接的游戏
- ✅ 使用白名单验证可嵌入域名
- ✅ 检查X-Frame-Options头确保可嵌入性
- ✅ 过滤掉新闻文章、公司介绍等无效内容

**白名单域名**：
- `html-classic.itch.zone` - itch.io的HTML5游戏嵌入域名
- `v6p9d9t4.ssl.hwcdn.net` - itch.io的CDN域名
- `uploads.ungrounded.net` - Newgrounds嵌入域名
- `gamejolt.net` - GameJolt嵌入域名
- `crazygames.com/embed` - CrazyGames嵌入
- `poki.com/embed` - Poki嵌入
- `kongregate.com/embed` - Kongregate嵌入

### 3. 移除重复游戏

```bash
python remove_duplicates.py
```

这个脚本会：
- ✅ 检测重复的游戏标题和URL
- ✅ 只保留第一个出现的游戏
- ✅ 重新编号游戏ID

### 4. 运行爬虫

#### 推荐：使用增强版爬虫（专门收集可嵌入游戏）

```bash
python enhanced_crawler.py
python merge_games.py
```

这个增强版爬虫专门设计用于收集可以直接在平台内运行的游戏，确保：
- ✅ 所有游戏都可以通过iframe嵌入
- ✅ 不需要跳转到外部链接
- ✅ 验证X-Frame-Options头，确保可嵌入性
- ✅ 过滤掉视频、广告等不适合的内容
- ✅ 验证游戏数据有效性

#### 标准爬虫

```bash
python game_crawler.py
```

这将从各个游戏网站爬取游戏数据，并将结果保存到`src/data/games.ts`文件中。同时，爬取的原始数据也会保存为JSON格式，方便查看和调试。

### 5. 修复文件格式

如果发现`games.ts`文件格式有问题，可以运行修复脚本：

```bash
python fix_games_file.py
```

这个脚本会自动修复文件格式，将游戏数据正确放入games数组中。

### 6. 一键爬取和修复

也可以使用组合脚本，一次完成爬取和修复：

```bash
python crawl_and_fix.py
```

## 推荐工作流程

### 解决外部链接跳转问题

如果发现游戏点击后跳转到外部链接，按以下步骤操作：

```bash
# 1. 严格清理，只保留真正可嵌入的游戏
python strict_clean_games.py

# 2. 移除重复游戏
python remove_duplicates.py

# 3. 如需要更多游戏，运行增强版爬虫
python enhanced_crawler.py
python merge_games.py

# 4. 再次去重（如果添加了新游戏）
python remove_duplicates.py
```

### 从零开始构建游戏库

```bash
# 1. 重建干净的文件
python rebuild_games_file.py

# 2. 运行增强版爬虫
python enhanced_crawler.py
python merge_games.py

# 3. 严格清理确保质量
python strict_clean_games.py

# 4. 移除重复
python remove_duplicates.py
```

## 游戏类型说明

### iframe类型游戏
- 通过iframe直接嵌入到页面中
- 游戏在iframe内运行，用户无需离开平台
- 支持的域名：`html-classic.itch.zone`、`gamejolt.com/embed`等

### static类型游戏
- HTML5游戏文件，可以下载到本地运行
- 通常是单个HTML文件或包含资源的游戏包
- 适合离线游玩

## 数据验证机制

所有爬虫现在都包含严格的数据验证：

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
- ✅ 可嵌入的iframe游戏
- ✅ 可下载的HTML5游戏文件
- ✅ 有效的游戏URL
- ✅ 通过白名单验证的域名

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

## 注意事项

1. **数据质量保证**：
   - 所有爬虫都包含数据验证机制
   - 自动过滤无效和不适合的内容
   - 确保收集的都是真正的游戏

2. **严格的URL验证**：
   - 使用白名单机制验证可嵌入域名
   - 检查X-Frame-Options头
   - 过滤掉所有外部链接跳转

3. 修复脚本会在修复前自动备份原始文件，备份文件保存为`src/data/games.ts.strict_backup`。

4. 爬虫结果会同时保存为JSON格式，方便查看和调试：
   - `scripts/crawled_games.json` - 标准爬虫结果
   - `scripts/enhanced_games.json` - 增强版爬虫结果

5. 如果遇到SSL证书问题，可以参考`install_dependencies.py`中的解决方案。

## 自定义配置

### 严格清理脚本配置

可以在`strict_clean_games.py`文件中修改：

- `EMBEDDABLE_DOMAINS` - 可嵌入的域名白名单
- `BLOCKED_DOMAINS` - 禁止的域名黑名单

### 增强版爬虫配置

可以在`enhanced_crawler.py`文件中修改：

- `HTML5_GAME_SITES` - 专门的HTML5游戏平台配置
- `embeddable_domains` - 可嵌入的域名列表

### 标准爬虫配置

可以在`game_crawler.py`文件中修改：

- `SEARCH_QUERIES` - 搜索引擎查询关键词
- `SEED_URLS` - 种子URL列表
- `CATEGORY_MAPPING` - 游戏分类映射
- `CATEGORY_ID_MAPPING` - 分类ID映射

## 日志

所有脚本都会生成日志文件，方便排查问题：

- `game_crawler.log` - 标准爬虫日志
- `enhanced_crawler.log` - 增强版爬虫日志
- `strict_clean_games.log` - 严格清理日志
- `remove_duplicates.log` - 去重脚本日志
- `fix_games_file.log` - 文件修复日志
- `clean_games.log` - 清理脚本日志
- `merge_games.log` - 合并脚本日志
- `crawl_and_fix.log` - 组合脚本日志 