# 测试逗号显示 - 使用文件输出
test_string = "centre drilling, drilling, milling"

with open('d:/python/ai部署/output_test.txt', 'w', encoding='utf-8') as f:
    f.write(f"原始字符串: {repr(test_string)}\n")
    f.write(f"显示内容: {test_string}\n")
    f.write(f"长度: {len(test_string)}\n")
    
    # 检查逗号是否存在
    if ',' in test_string:
        f.write("包含逗号!\n")
    else:
        f.write("不包含逗号!\n")
    
    # 替换逗号为显式标记
    replaced = test_string.replace(',', '[COMMA]')
    f.write(f"替换后: {replaced}\n")