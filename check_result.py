import os, sys, django
sys.path.append('d:/python/ai部署/mynewproject')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mynewproject.settings')
django.setup()

from imageprocessor.models import ProcessedImage

# 获取最新的处理记录
latest = ProcessedImage.objects.order_by('-uploaded_at').first()
if latest:
    print('最新记录ID:', latest.id)
    print('状态:', latest.status)
    print('结果类型:', type(latest.result))
    print('结果长度:', len(latest.result))
    print('\n结果内容:')
    print(latest.result)
else:
    print('没有找到处理记录')