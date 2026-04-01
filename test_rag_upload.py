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
    name='test_rag_image.jpg',
    content=image_data,
    content_type='image/jpeg'
)

# 模拟上传
client = Client()
response = client.post('/', {'image': uploaded_file})

print('Status:', response.status_code)
print('Redirect to:', response.url if response.status_code == 302 else 'N/A')