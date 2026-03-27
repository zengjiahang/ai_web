# 检查文件内容
with open('d:/python/ai部署/mynewproject/imageprocessor/views.py', 'rb') as f:
    lines = f.readlines()

line = lines[250]  # 第251行
print('Line 251 bytes:', line)
print()
print('Position 39:', line[39], 'hex:', hex(line[39]))
print('Position 40:', line[40], 'hex:', hex(line[40]))