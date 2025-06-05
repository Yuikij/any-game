# 集成游戏爬虫使用说明

## 📋 概述

`integrated_game_crawler.py` 是一个功能完整的游戏爬虫脚本，集成了之前所有的优化功能：

- 🌐 多平台爬取 (itch.io, Newgrounds, 等)
- 🔍 API搜索支持 (SerpAPI)
- 🌐 代理支持
- 🖼️ 自动缩略图生成
- ⚡ 并发处理
- 🎯 智能去重
- 📊 详细统计

## 🚀 快速开始

### 1. 安装依赖

```bash
pip install requests beautifulsoup4 lxml pillow aiohttp
```

### 2. 基本使用

```bash
# 快速模式，爬取30个游戏
python scripts/integrated_game_crawler.py --mode quick --target 30

# 完整模式，爬取50个游戏
python scripts/integrated_game_crawler.py --mode full --target 50

# API搜索模式
python scripts/integrated_game_crawler.py --mode api --target 20
```

## 📖 详细使用指南

### 命令行参数

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `--mode` | str | `full` | 爬取模式: `quick`/`full`/`api` |
| `--target` | int | `50` | 目标游戏数量 |
| `--use-proxy` | flag | False | 启用代理 |
| `--generate-thumbnails` | flag | True | 生成缩略图 |
| `--api-search` | flag | False | 启用API搜索 |
| `--platforms` | str | `itch.io,newgrounds` | 指定平台，用逗号分隔 |
| `--delay` | str | `0.5-1.0` | 请求延迟范围(秒) |
| `--workers` | int | `3` | 并发工作线程数 |

### 爬取模式说明

#### 1. 快速模式 (quick)
- 主要从 itch.io 平台爬取
- 速度最快，适合快速获取游戏
- 推荐用于测试或小量爬取

```bash
python scripts/integrated_game_crawler.py --mode quick --target 20
```

#### 2. 完整模式 (full)
- 多平台并发爬取
- 可选API搜索补充
- 功能最全面，推荐用于生产环境

```bash
python scripts/integrated_game_crawler.py --mode full --target 50 --api-search
```

#### 3. API模式 (api)
- 主要通过搜索API获取游戏
- 需要配置API密钥
- 适合获取特定类型游戏

```bash
python scripts/integrated_game_crawler.py --mode api --target 30 --api-search
```

## ⚙️ 配置文件

### 代理配置

创建 `config/proxies.txt` 文件：

```
http://127.0.0.1:8080
http://username:password@proxy.example.com:8888
```

使用代理：
```bash
python scripts/integrated_game_crawler.py --use-proxy
```

### API密钥配置

创建 `config/api_keys.json` 文件：

```json
{
  "serp_api_key": "your_serpapi_key_here"
}
```

使用API搜索：
```bash
python scripts/integrated_game_crawler.py --api-search
```

## 🎨 缩略图生成

脚本自动为游戏生成精美的缩略图：

- 8种颜色主题
- 4种几何图案
- 自动文字布局
- 300x200像素尺寸

禁用缩略图生成：
```bash
python scripts/integrated_game_crawler.py --generate-thumbnails=false
```

## 🌐 支持的平台

目前支持的游戏平台：

1. **itch.io** - HTML5游戏平台
2. **Newgrounds** - Flash/HTML5游戏平台
3. **Kongregate** - 网页游戏平台 (实验性)
4. **CrazyGames** - 网页游戏平台 (实验性)
5. **Poki** - 网页游戏平台 (实验性)

指定特定平台：
```bash
python scripts/integrated_game_crawler.py --platforms itch.io,newgrounds
```

## 📊 输出和日志

### 控制台输出
脚本运行时会显示详细的进度信息：
- 平台爬取状态
- 找到的游戏数量
- 缩略图生成进度
- 最终统计结果

### 日志文件
详细日志保存在 `game_crawler.log` 文件中。

### 游戏数据
爬取的游戏保存在 `src/data/games.ts` 文件中，原文件会自动备份。

## 🎯 使用示例

### 示例1：快速获取20个游戏
```bash
python scripts/integrated_game_crawler.py --mode quick --target 20
```

### 示例2：完整爬取，使用代理和API
```bash
python scripts/integrated_game_crawler.py \
  --mode full \
  --target 50 \
  --use-proxy \
  --api-search \
  --workers 5
```

### 示例3：仅从itch.io爬取，自定义延迟
```bash
python scripts/integrated_game_crawler.py \
  --platforms itch.io \
  --target 30 \
  --delay 1.0-2.0
```

### 示例4：API搜索特定游戏
```bash
python scripts/integrated_game_crawler.py \
  --mode api \
  --target 15 \
  --api-search
```

## 🔧 高级配置

### 性能调优

1. **并发数调整**
   ```bash
   --workers 5  # 增加并发线程
   ```

2. **延迟调整**
   ```bash
   --delay 0.3-0.8  # 减少延迟，提高速度
   --delay 2.0-5.0  # 增加延迟，更礼貌
   ```

3. **平台优化**
   ```bash
   --platforms itch.io  # 只爬取最稳定的平台
   ```

### 错误处理

脚本内置了完善的错误处理：
- 网络超时重试
- 403/404错误优雅处理
- 平台不可用时的回退机制
- 数据验证和清理

## 📈 性能指标

在标准配置下：
- **速度**: 每分钟约10-20个游戏
- **成功率**: 80-90%
- **内存使用**: 约50-100MB
- **网络流量**: 每个游戏约50-200KB

## 🚨 注意事项

1. **尊重网站规则**
   - 不要设置过低的延迟
   - 合理控制并发数
   - 遵守robots.txt

2. **网络环境**
   - 确保网络连接稳定
   - 某些平台可能需要代理访问
   - API可能有速率限制

3. **数据质量**
   - 脚本会自动去重
   - 无效游戏会被过滤
   - 建议定期清理数据

## 🛠️ 故障排除

### 常见问题

1. **没有找到游戏**
   - 检查网络连接
   - 尝试使用代理
   - 降低并发数

2. **缩略图生成失败**
   - 确保安装了Pillow库
   - 检查目录权限
   - 查看详细错误日志

3. **API搜索无结果**
   - 检查API密钥配置
   - 确认API额度充足
   - 验证网络连接

### 调试模式

启用详细日志：
```bash
# 编辑脚本，将日志级别改为DEBUG
logging.basicConfig(level=logging.DEBUG, ...)
```

## 📞 技术支持

如遇到问题，请检查：
1. 错误日志 (`game_crawler.log`)
2. 网络连接状态
3. 依赖库版本
4. 配置文件格式

---

## 🎉 总结

集成游戏爬虫提供了完整的游戏爬取解决方案，支持多种模式和配置选项。通过合理的参数配置，可以高效、稳定地获取大量游戏数据，同时自动生成精美的缩略图。

推荐的使用流程：
1. 首先用快速模式测试
2. 配置代理和API密钥
3. 使用完整模式批量爬取
4. 定期运行维护数据质量 