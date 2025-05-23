#!/bin/bash

echo "========================================"
echo "         游戏爬虫脚本运行器"
echo "========================================"
echo

# 检查Python环境
echo "正在检查Python环境..."
if ! command -v python3 &> /dev/null; then
    echo "错误：未找到Python3，请先安装Python 3.7+"
    exit 1
fi

echo "Python环境检查通过"
echo

# 检查依赖包
echo "正在检查依赖包..."
if ! python3 -c "import requests" &> /dev/null; then
    echo "正在安装依赖包..."
    pip3 install -r requirements.txt
    if [ $? -ne 0 ]; then
        echo "错误：依赖包安装失败"
        exit 1
    fi
else
    echo "依赖包检查通过"
fi

echo
echo "请选择运行模式："
echo "1. 快速爬取（推荐，约10个游戏）"
echo "2. 完整爬取（约30个游戏，耗时较长）"
echo "3. 退出"
echo
read -p "请输入选择 (1-3): " choice

case $choice in
    1)
        echo
        echo "开始快速爬取..."
        python3 quick_crawl.py
        ;;
    2)
        echo
        echo "开始完整爬取..."
        python3 game_crawler.py
        ;;
    3)
        echo "退出程序"
        exit 0
        ;;
    *)
        echo "无效选择，退出程序"
        exit 1
        ;;
esac

echo
echo "爬取完成！"
echo "请检查 src/data/games.ts 文件查看新添加的游戏"
echo 