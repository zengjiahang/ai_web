# 测试逗号显示
test_string = "centre drilling, drilling, milling"
print("原始字符串:", repr(test_string))
print("显示内容:", test_string)

# 检查每个字符
for i, char in enumerate(test_string):
    print(f"{i}: {char!r} (ord={ord(char)})")