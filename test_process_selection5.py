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

# 从数据库中获取最新记录
latest_image = ProcessedImage.objects.order_by('-id').first()
if latest_image:
    image_id = latest_image.id
    print('Image ID:', image_id)
    
    # 测试保存工艺选择API - 添加sequence字段
    test_selections = [
        {
            'feature_name': 'F1',
            'operation': 'milling',
            'prior_operations': 'none',
            'sequence': 0,
            'machine': 'm1',
            'tool': 't1,t2',
            'is_chamfer_second': False
        },
        {
            'feature_name': 'F1',
            'operation': 'milling',
            'prior_operations': 'none',
            'sequence': 1,
            'machine': 'm2',
            'tool': 't3',
            'is_chamfer_second': False
        },
        {
            'feature_name': 'F2',
            'operation': 'milling',
            'prior_operations': 'none',
            'sequence': 0,
            'machine': 'm3',
            'tool': 't4,t5',
            'is_chamfer_second': False
        },
        {
            'feature_name': 'F2',
            'operation': 'milling',
            'prior_operations': 'none',
            'sequence': 1,
            'machine': 'm4',
            'tool': 't6',
            'is_chamfer_second': False
        },
        {
            'feature_name': 'F3',
            'operation': 'drilling',
            'prior_operations': 'centre drilling, milling',
            'sequence': 0,
            'machine': 'm1,m2',
            'tool': 't7,t8',
            'is_chamfer_second': False
        },
        {
            'feature_name': 'F3',
            'operation': 'centre drilling',
            'prior_operations': 'none',
            'sequence': 0,
            'machine': 'm3',
            'tool': 't10',
            'is_chamfer_second': False
        },
        {
            'feature_name': 'F3',
            'operation': 'milling',
            'prior_operations': 'centre drilling, drilling, milling',
            'sequence': 0,
            'machine': 'm1',
            'tool': 't1',
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
    get_response = client.get(f'/api/get-process-selections/?image_id={image_id}')
    print('Get selections after save status:', get_response.status_code)
    if get_response.status_code == 200:
        result = get_response.json()
        print('Number of selections:', len(result['selections']))
        for selection in result['selections']:
            print(f"  {selection['feature_name']}[{selection['sequence']}] - {selection['operation']}: machine={selection['machine']}, tool={selection['tool']}")
    else:
        print('Get selections error:', get_response.content)
else:
    print('Could not find any images in database')