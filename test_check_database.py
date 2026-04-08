import os, sys, django, re, json
sys.path.append('d:/python/ai部署/mynewproject')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mynewproject.settings')
django.setup()

from django.test import Client
from django.core.files.uploadedfile import SimpleUploadedFile
from imageprocessor.models import ProcessedImage, ProcessSelection

# 从数据库中获取最新记录
latest_image = ProcessedImage.objects.order_by('-id').first()
if latest_image:
    image_id = latest_image.id
    print('Image ID:', image_id)
    
    # 直接查看数据库中的数据
    selections = ProcessSelection.objects.filter(processed_image=latest_image).order_by('feature_name', 'sequence', 'operation')
    print('Database selections:')
    for selection in selections:
        print(f"  {selection.feature_name}[{selection.sequence}] - {selection.operation}:")
        print(f"    machine: '{selection.machine}'")
        print(f"    tool: '{selection.tool}'")
        print(f"    tool length: {len(selection.tool)}")
        print(f"    tool contains comma: {',' in selection.tool}")
        print()
else:
    print('Could not find any images in database')