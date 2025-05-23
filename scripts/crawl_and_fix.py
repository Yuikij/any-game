#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
游戏爬虫和文件修复的组合脚本
先运行爬虫获取游戏数据，然后修复games.ts文件格式
"""

import os
import sys
import time
import logging
import subprocess
from datetime import datetime

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('crawl_and_fix.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# 项目配置
SCRIPTS_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPTS_DIR)
CRAWLER_SCRIPT = os.path.join(SCRIPTS_DIR, 'game_crawler.py')
FIX_SCRIPT = os.path.join(SCRIPTS_DIR, 'fix_games_file.py')

def run_script(script_path, timeout=600):
    """运行Python脚本并返回结果"""
    try:
        logger.info(f"开始运行脚本: {os.path.basename(script_path)}")
        
        # 构建命令
        python_cmd = sys.executable  # 当前Python解释器路径
        cmd = [python_cmd, script_path]
        
        # 运行脚本
        start_time = time.time()
        result = subprocess.run(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            timeout=timeout
        )
        
        # 检查结果
        elapsed_time = time.time() - start_time
        if result.returncode == 0:
            logger.info(f"脚本运行成功，耗时: {elapsed_time:.2f}秒")
            return True, result.stdout
        else:
            logger.error(f"脚本运行失败，退出码: {result.returncode}")
            logger.error(f"错误输出: {result.stderr}")
            return False, result.stderr
            
    except subprocess.TimeoutExpired:
        logger.error(f"脚本运行超时 (>{timeout}秒)")
        return False, "脚本运行超时"
    except Exception as e:
        logger.error(f"运行脚本时出错: {e}")
        return False, str(e)

def main():
    """主函数"""
    logger.info("=" * 60)
    logger.info(f"开始游戏爬虫和文件修复流程 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info("=" * 60)
    
    # 1. 运行爬虫脚本
    logger.info("步骤1: 运行游戏爬虫...")
    crawler_success, crawler_output = run_script(CRAWLER_SCRIPT, timeout=900)  # 15分钟超时
    
    if not crawler_success:
        logger.error("爬虫运行失败，流程终止")
        return
    
    # 2. 运行文件修复脚本
    logger.info("步骤2: 修复games.ts文件格式...")
    fix_success, fix_output = run_script(FIX_SCRIPT)
    
    if not fix_success:
        logger.error("文件修复失败")
        return
    
    logger.info("=" * 60)
    logger.info("爬虫和文件修复流程完成！")
    logger.info("=" * 60)

if __name__ == '__main__':
    main() 