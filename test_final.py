import os, sys, django
sys.path.append('d:/python/ai部署/mynewproject')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mynewproject.settings')
django.setup()

from imageprocessor.views import format_features_to_table

# 模拟1个槽、1个孔
test_features = {'slot': 1, 'hole': 1, 'chamfer': 0, 'shoulder': 0, 'step': 0}
table_data = format_features_to_table(test_features)

# 检查逗号
for row in table_data:
    print(f'{row[0]}: {row[2]}')
    comma = ','
    print(f'  Contains comma: {comma in row[2]}')
    hex_list = [hex(ord(c)) for c in row[2]]
    print(f'  Bytes: {hex_list}')