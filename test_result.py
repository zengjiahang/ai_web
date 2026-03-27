import os, sys, django
sys.path.append('d:/python/ai部署/mynewproject')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mynewproject.settings')
django.setup()

from imageprocessor.models import ProcessedImage

# 获取最新上传的图片
latest = ProcessedImage.objects.order_by('-id').first()
print(f'图片ID: {latest.id}')
print(f'状态: {latest.status}')
print(f'结果长度: {len(latest.result) if latest.result else 0}')
if latest.result:
    print('结果预览:')
    print(latest.result[:500])
    print('...')
else:
    print('无结果')

# 访问结果页面
from django.test import Client
client = Client()
response = client.get(f'/result/{latest.id}/')
print(f'\\n结果页面状态码: {response.status_code}')
if response.status_code == 200:
    # 检查是否包含表格
    content = response.content.decode('utf-8')
    if 'table-bordered' in content:
        print('✅ 页面包含表格')
    else:
        print('❌ 页面不包含表格')
        
    # 检查特征提取
    if 'slot' in content and 'hole' in content:
        print('✅ 页面包含特征信息')
    else:
        print('❌ 页面不包含特征信息')
else:
    print('❌ 页面访问失败')