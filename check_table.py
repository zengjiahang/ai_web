import os, sys, django
sys.path.append('d:/python/ai部署/mynewproject')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mynewproject.settings')
django.setup()

from django.test import Client
client = Client()

# 获取最新结果页面
response = client.get('/result/36/')
content = response.content.decode('utf-8')

# 提取表格内容
import re
table_match = re.search(r'<table class="table table-bordered.*?</table>', content, re.DOTALL)
if table_match:
    print('=== 表格HTML ===')
    print(table_match.group())
else:
    print('未找到表格')
    
# 保存完整页面
with open('d:/python/ai部署/test_page.html', 'w', encoding='utf-8') as f:
    f.write(content)
print('\\n页面已保存到 d:/python/ai部署/test_page.html')