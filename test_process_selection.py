import os, sys, django
sys.path.append('d:/python/ai部署/mynewproject')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mynewproject.settings')
django.setup()

from django.test import Client
from django.core.files.uploadedfile import SimpleUploadedFile

# 读取测试图片
with open('d:/python/ai部署/图片/微信图片_20251123111536_70_19.jpg', 'rb') as f:
    image_data = f.read()

# 创建上传文件
uploaded_file = SimpleUploadedFile(
    name='test_process_selection.jpg',
    content=image_data,
    content_type='image/jpeg'
)

# 模拟上传
client = Client()
response = client.post('/', {'image': uploaded_file})

print('Status:', response.status_code)
print('Redirect to:', response.url if response.status_code == 302 else 'N/A')

# 如果是200，提取图片ID
if response.status_code == 200:
    # 尝试从响应中提取图片ID
    import re
    match = re.search(r'/result/(\d+)/', str(response.content))
    if match:
        image_id = match.group(1)
        print('Image ID:', image_id)
        
        # 测试获取工艺选择API
        get_response = client.get(f'/api/get-process-selections/?image_id={image_id}')
        print('Get selections status:', get_response.status_code)
        if get_response.status_code == 200:
            print('Get selections content:', get_response.json())
        else:
            print('Get selections error:', get_response.content)
    else:
        print('Could not extract image ID from response')