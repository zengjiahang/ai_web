import os, sys, django, re, json
sys.path.append('d:/python/ai部署/mynewproject')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mynewproject.settings')
django.setup()

from django.test import Client
from django.core.files.uploadedfile import SimpleUploadedFile
from imageprocessor.models import ProcessedImage

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
print('Content type:', response.get('Content-Type'))

# 如果是200，提取图片ID
if response.status_code == 200:
    content = response.content.decode('utf-8')
    
    # 尝试多种方式提取图片ID
    # 方法1：从JavaScript中提取
    match1 = re.search(r'image_id["\s:]+(\d+)', content)
    if match1:
        image_id = match1.group(1)
        print('Image ID (method 1):', image_id)
    else:
        # 方法2：从URL中提取
        match2 = re.search(r'/result/(\d+)/', content)
        if match2:
            image_id = match2.group(1)
            print('Image ID (method 2):', image_id)
        else:
            # 方法3：从数据库中获取最新记录
            latest_image = ProcessedImage.objects.order_by('-id').first()
            if latest_image:
                image_id = latest_image.id
                print('Image ID (method 3 - latest):', image_id)
            else:
                print('Could not find any images in database')
                image_id = None
    
    if image_id:
        print('Testing with image_id:', image_id)
        
        # 测试获取工艺选择API
        get_response = client.get(f'/api/get-process-selections/?image_id={image_id}')
        print('Get selections status:', get_response.status_code)
        if get_response.status_code == 200:
            print('Get selections content:', get_response.json())
        else:
            print('Get selections error:', get_response.content)
        
        # 测试保存工艺选择API
        test_selections = [
            {
                'feature_name': 'F1',
                'operation': 'milling',
                'prior_operations': 'none',
                'machine': 'm1',
                'tool': 't1,t2',
                'is_chamfer_second': False
            },
            {
                'feature_name': 'F1',
                'operation': 'milling',
                'prior_operations': 'none',
                'machine': 'm2',
                'tool': 't3',
                'is_chamfer_second': False
            }
        ]
        
        save_response = client.post(
            '/api/save-process-selections/',
            data=json.dumps({'image_id': image_id, 'selections': test_selections}),
            content_type='application/json'
        )
        print('Save selections status:', save_response.status_code)
        if save_response.status_code == 200:
            print('Save selections content:', save_response.json())
        else:
            print('Save selections error:', save_response.content)
        
        # 再次获取以验证保存
        get_response2 = client.get(f'/api/get-process-selections/?image_id={image_id}')
        print('Get selections after save status:', get_response2.status_code)
        if get_response2.status_code == 200:
            print('Get selections after save content:', get_response2.json())