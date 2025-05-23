@echo off
chcp 65001 >nul
echo ========================================
echo          游戏爬虫脚本运行器
echo ========================================
echo.

echo 正在检查Python环境...
python --version >nul 2>&1
if errorlevel 1 (
    echo 错误：未找到Python，请先安装Python 3.7+
    pause
    exit /b 1
)

echo Python环境检查通过
echo.

echo 正在检查依赖包...
pip show requests >nul 2>&1
if errorlevel 1 (
    echo 正在安装依赖包...
    pip install -r requirements.txt
    if errorlevel 1 (
        echo 错误：依赖包安装失败
        pause
        exit /b 1
    )
) else (
    echo 依赖包检查通过
)

echo.
echo 请选择运行模式：
echo 1. 快速爬取（推荐，约10个游戏）
echo 2. 完整爬取（约30个游戏，耗时较长）
echo 3. 退出
echo.
set /p choice=请输入选择 (1-3): 

if "%choice%"=="1" (
    echo.
    echo 开始快速爬取...
    python quick_crawl.py
) else if "%choice%"=="2" (
    echo.
    echo 开始完整爬取...
    python game_crawler.py
) else if "%choice%"=="3" (
    echo 退出程序
    exit /b 0
) else (
    echo 无效选择，退出程序
    exit /b 1
)

echo.
echo 爬取完成！
echo 请检查 src/data/games.ts 文件查看新添加的游戏
echo.
pause 