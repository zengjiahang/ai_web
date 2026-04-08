import os, sys, django, re, json
sys.path.append('d:/python/ai部署/mynewproject')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mynewproject.settings')
django.setup()

from django.test import Client
from django.core.files.uploadedfile import SimpleUploadedFile
from imageprocessor.models import ProcessedImage

# 从数据库中获取最新记录
latest_image = ProcessedImage.objects.order_by('-id').first()
if latest_image:
    image_id = latest_image.id
    print('Image ID:', image_id)
    
    # 测试获取API
    client = Client()
    get_response = client.get(f'/api/get-process-selections/?image_id={image_id}')
    print('Get selections status:', get_response.status_code)
    
    if get_response.status_code == 200:
        result = get_response.json()
        print('Raw JSON response:')
        print(result)
        print()
        
        print('Formatted output:')
        for selection in result['selections']:
            print(f"  {selection['feature_name']}[{selection['sequence']}] - {selection['operation']}:")
            print(f"    machine: '{selection['machine']}'")
            print(f"    tool: '{selection['tool']}'")
            print()
else:
    print('Could not find any images in database')