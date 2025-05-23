#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
依赖包安装脚本 - 解决网络连接问题
提供多种方式安装所需的Python包
"""

import subprocess
import sys
import os

def run_command(command):
    """运行命令并返回结果"""
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        return result.returncode == 0, result.stdout, result.stderr
    except Exception as e:
        return False, "", str(e)

def install_with_pip():
    """使用pip安装"""
    packages = ['beautifulsoup4', 'requests', 'tenacity']
    
    # 尝试多个镜像源
    mirrors = [
        '',  # 默认源
        '-i https://pypi.tuna.tsinghua.edu.cn/simple/',  # 清华源
        '-i https://pypi.douban.com/simple/',  # 豆瓣源
        '-i https://mirrors.aliyun.com/pypi/simple/',  # 阿里源
        '--trusted-host pypi.org --trusted-host pypi.python.org --trusted-host files.pythonhosted.org'  # 信任主机
    ]
    
    for mirror in mirrors:
        print(f"\n尝试使用{'默认源' if not mirror else '镜像源'}安装...")
        command = f"pip install {' '.join(packages)} {mirror}"
        success, stdout, stderr = run_command(command)
        
        if success:
            print("✅ 安装成功！")
            return True
        else:
            print(f"❌ 安装失败: {stderr}")
    
    return False

def check_packages():
    """检查包是否已安装"""
    packages = ['bs4', 'requests', 'tenacity']
    missing = []
    
    for package in packages:
        try:
            __import__(package)
            print(f"✅ {package} 已安装")
        except ImportError:
            print(f"❌ {package} 未安装")
            missing.append(package)
    
    return len(missing) == 0, missing

def create_offline_requirements():
    """创建离线安装包信息"""
    print("\n📦 创建离线安装说明...")
    
    offline_guide = """
# 离线安装指南

如果网络连接有问题，您可以：

## 方法1：使用离线演示（推荐）
直接运行 offline_demo.py，无需安装额外依赖：
```
python offline_demo.py
```

## 方法2：手动下载安装包
1. 在有网络的电脑上下载以下文件：
   - beautifulsoup4-4.12.2-py3-none-any.whl
   - requests-2.31.0-py3-none-any.whl
   - tenacity-8.2.3-py3-none-any.whl

2. 复制到当前电脑，然后运行：
```
pip install beautifulsoup4-4.12.2-py3-none-any.whl
pip install requests-2.31.0-py3-none-any.whl
pip install tenacity-8.2.3-py3-none-any.whl
```

## 方法3：使用conda（如果已安装）
```
conda install beautifulsoup4 requests tenacity
```

## 方法4：禁用SSL验证（不推荐）
```
pip install beautifulsoup4 requests tenacity --trusted-host pypi.org --trusted-host pypi.python.org --trusted-host files.pythonhosted.org
```
"""
    
    with open('offline_install_guide.txt', 'w', encoding='utf-8') as f:
        f.write(offline_guide)
    
    print("✅ 离线安装指南已保存到 offline_install_guide.txt")

def main():
    """主函数"""
    print("🔧 Python依赖包安装工具")
    print("=" * 50)
    
    # 检查当前状态
    print("\n📋 检查当前包状态...")
    all_installed, missing = check_packages()
    
    if all_installed:
        print("\n🎉 所有依赖包都已安装！")
        print("您可以直接运行：")
        print("  python game_crawler.py    # 完整爬虫")
        print("  python quick_crawl.py     # 快速爬虫")
        print("  python offline_demo.py    # 离线演示")
        return
    
    print(f"\n⚠️  缺少以下包: {', '.join(missing)}")
    
    # 尝试安装
    print("\n🚀 开始安装依赖包...")
    if install_with_pip():
        print("\n🎉 所有依赖包安装完成！")
        print("现在您可以运行完整的爬虫脚本了。")
    else:
        print("\n❌ 自动安装失败")
        print("正在创建离线安装指南...")
        create_offline_requirements()
        print("\n💡 建议：")
        print("1. 先使用离线演示验证功能：python offline_demo.py")
        print("2. 参考 offline_install_guide.txt 进行手动安装")
        print("3. 或者联系网络管理员解决SSL连接问题")

if __name__ == '__main__':
    main() 