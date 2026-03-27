# 测试逗号问题
s1 = "centre drilling, drilling, milling"
s2 = "centre drilling, milling"
s3 = "milling"

print(f"s1: {s1}")
print(f"s2: {s2}")
print(f"s3: {s3}")

# 测试列表
test_list = [
    ["F1", "milling", s1],
    ["F2", "drilling", s2],
    ["F3", "centre drilling", s3]
]

for row in test_list:
    print(row)