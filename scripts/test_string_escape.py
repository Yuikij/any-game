#!/usr/bin/env python3
"""
字符串转义测试脚本
验证集成爬虫的字符串转义功能
"""

def escape_string_for_js(text):
    """转义字符串用于JavaScript/TypeScript输出"""
    if not text:
        return text
    
    # 转义特殊字符，反斜杠必须首先转义
    text = text.replace('\\', '\\\\')  # 反斜杠
    text = text.replace("'", "\\'")    # 单引号
    text = text.replace('"', '\\"')    # 双引号  
    text = text.replace('\n', '\\n')   # 换行符
    text = text.replace('\r', '\\r')   # 回车符
    text = text.replace('\t', '\\t')   # 制表符
    
    return text

def test_string_escape():
    """测试字符串转义功能"""
    print("🧪 字符串转义测试")
    print("=" * 50)
    
    test_cases = [
        ("Mr. Magpie's Harmless Card Game", "包含单引号的标题"),
        ('Game with "quotes"', "包含双引号的标题"),
        ("Game\nwith\nnewlines", "包含换行符的标题"),
        ("Game\twith\ttabs", "包含制表符的标题"),
        ("Game\\with\\backslashes", "包含反斜杠的标题"),
        ("Complex's \"Game\" with\nmany\tspecial\\chars", "包含多种特殊字符的标题"),
        ("", "空字符串"),
        ("Normal Game Title", "正常标题"),
    ]
    
    for original, description in test_cases:
        escaped = escape_string_for_js(original)
        print(f"\n📝 测试: {description}")
        print(f"原始: {repr(original)}")
        print(f"转义后: {repr(escaped)}")
        
        # 生成TypeScript代码片段
        ts_code = f"title: '{escaped}'"
        print(f"TS代码: {ts_code}")
        
        # 验证转义是否正确（检查单引号是否被转义）
        if "'" in original and "\\'" not in escaped:
            print("❌ 警告：单引号未被正确转义！")
        else:
            print("✅ 转义正确")

def generate_sample_game():
    """生成一个包含特殊字符的示例游戏对象"""
    game = {
        'id': 'test_game_001',
        'title': "Mr. Magpie's \"Special\" Game\nwith tabs\tand backslashes\\",
        'description': 'A test game with various special characters: \'"\\n\\t\\r',
        'category': '休闲',
        'categoryId': '1',
        'thumbnail': '/games/thumbnails/auto_game_001.jpg',
        'path': '/games/test_game_001',
        'featured': False,
        'type': 'iframe',
        'iframeUrl': 'https://example.com/game\'s/path',
        'addedAt': '2025-06-05',
        'tags': ['HTML5', "Test's Game", 'Special "Chars"']
    }
    
    print("\n🎮 示例游戏对象生成")
    print("=" * 50)
    
    # 转义所有字符串字段
    title = escape_string_for_js(game['title'])
    description = escape_string_for_js(game['description'])
    category = escape_string_for_js(game['category'])
    thumbnail = escape_string_for_js(game['thumbnail'])
    path = escape_string_for_js(game['path'])
    iframe_url = escape_string_for_js(game['iframeUrl'])
    
    # 生成TypeScript代码
    ts_code = f"""  {{
    id: '{game['id']}',
    title: '{title}',
    description: '{description}',
    category: '{category}',
    categoryId: '{game['categoryId']}',
    thumbnail: '{thumbnail}',
    path: '{path}',
    featured: {str(game['featured']).lower()},
    type: '{game['type']}',
    iframeUrl: '{iframe_url}',
    addedAt: '{game['addedAt']}',
    tags: {game['tags']}
  }}"""
    
    print("生成的TypeScript代码:")
    print(ts_code)
    
    return ts_code

def validate_typescript_syntax(ts_code):
    """验证TypeScript代码语法"""
    print("\n🔍 语法验证")
    print("=" * 50)
    
    # 简单的语法检查
    issues = []
    
    # 检查未转义的单引号
    lines = ts_code.split('\n')
    for i, line in enumerate(lines, 1):
        if "'" in line:
            # 检查是否有未转义的单引号
            in_string = False
            escaped = False
            for j, char in enumerate(line):
                if char == "'" and not escaped:
                    if in_string:
                        # 字符串结束
                        in_string = False
                    else:
                        # 字符串开始，检查前面是否有未转义的单引号
                        if j > 0 and j < len(line) - 1:
                            # 在字符串中间发现单引号，检查是否转义
                            if line[j-1] != '\\':
                                issues.append(f"第{i}行可能有未转义的单引号: {line.strip()}")
                        in_string = True
                elif char == '\\':
                    escaped = not escaped
                else:
                    escaped = False
    
    if issues:
        print("❌ 发现潜在问题:")
        for issue in issues:
            print(f"  - {issue}")
    else:
        print("✅ 语法验证通过")

def main():
    """主函数"""
    print("🎯 字符串转义功能验证")
    print("目的：确保游戏标题中的特殊字符正确转义")
    print()
    
    # 基础转义测试
    test_string_escape()
    
    # 生成示例游戏
    ts_code = generate_sample_game()
    
    # 验证语法
    validate_typescript_syntax(ts_code)
    
    print("\n🎉 测试完成！")
    print("请确保集成爬虫正确处理了所有特殊字符。")

if __name__ == "__main__":
    main() 