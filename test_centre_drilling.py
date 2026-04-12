import os, sys, django, re, json
sys.path.append('d:/python/ai部署/mynewproject')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mynewproject.settings')
django.setup()

from django.test import Client
from django.core.files.uploadedfile import SimpleUploadedFile
from imageprocessor.models import ProcessedImage

print("=" * 70)
print("测试Centre drilling显示")
print("=" * 70)

# 读取测试图片
with open('d:/python/ai部署/图片/微信图片_20251123111536_70_19.jpg', 'rb') as f:
    image_data = f.read()

# 创建上传文件
uploaded_file = SimpleUploadedFile(
    name='test_centre_drilling.jpg',
    content=image_data,
    content_type='image/jpeg'
)

# 模拟上传
client = Client()
response = client.post('/', {'image': uploaded_file})

print(f"\n1. 图片上传状态: {response.status_code}")

# 从数据库中获取最新记录
latest_image = ProcessedImage.objects.order_by('-id').first()
if latest_image:
    image_id = latest_image.id
    print(f"2. 图片ID: {image_id}")
    
    # 访问结果页面
    result_response = client.get(f'/result/{image_id}/')
    print(f"3. 结果页面状态: {result_response.status_code}")
    
    if result_response.status_code == 200:
        content = result_response.content.decode('utf-8')
        
        # 检查页面中是否包含centre drilling
        if 'centre drilling' in content.lower():
            print("✓ 页面包含centre drilling")
        else:
            print("✗ 页面不包含centre drilling")
        
        # 检查是否有machine-selector
        if 'machine-selector' in content:
            print("✓ 页面包含machine-selector")
        else:
            print("✗ 页面不包含machine-selector")
        
        # 检查是否有tool-selector
        if 'tool-selector' in content:
            print("✓ 页面包含tool-selector")
        else:
            print("✗ 页面不包含tool-selector")
        
        # 检查是否有MACHINE_TOOL_CONFIG
        if 'MACHINE_TOOL_CONFIG' in content:
            print("✓ 页面包含MACHINE_TOOL_CONFIG")
        else:
            print("✗ 页面不包含MACHINE_TOOL_CONFIG")
        
        # 检查是否有centre drilling的机器选项
        if 'm1' in content and 'm2' in content and 'm3' in content:
            print("✓ 页面包含机器选项m1, m2, m3")
        else:
            print("✗ 页面缺少机器选项")
        
        # 检查是否有t10
        if 't10' in content:
            print("✓ 页面包含t10")
        else:
            print("✗ 页面不包含t10")
        
        # 检查是否有checkbox
        if 'type="checkbox"' in content:
            print("✓ 页面包含checkbox")
        else:
            print("✗ 页面不包含checkbox")
        
        print("\n4. 保存centre drilling的选择")
        # 测试保存centre drilling的选择
        test_selections = [
            {
                'feature_name': 'F3',
                'operation': 'centre drilling',
                'prior_operations': 'none',
                'sequence': 0,
                'machine': 'm1,m2,m3',
                'tool': 't10',
                'is_chamfer_second': False
            }
        ]
        
        save_response = client.post(
            '/api/save-process-selections/',
            data=json.dumps({'image_id': image_id, 'selections': test_selections}),
            content_type='application/json'
        )
        print(f"5. 保存状态: {save_response.status_code}")
        
        if save_response.status_code == 200:
            print("✓ 保存成功")
        else:
            print(f"✗ 保存失败: {save_response.content}")
        
        # 验证保存的数据
        get_response = client.get(f'/api/get-process-selections/?image_id={image_id}')
        print(f"6. 获取选择状态: {get_response.status_code}")
        
        if get_response.status_code == 200:
            result = get_response.json()
            if result['selections']:
                centre_drilling = result['selections'][0]
                print(f"✓ Centre drilling: machine={centre_drilling['machine']}, tool={centre_drilling['tool']}")
                assert centre_drilling['tool'] == 't10', f"Tool应该是t10，实际是{centre_drilling['tool']}"
                assert centre_drilling['machine'] == 'm1,m2,m3', f"Machine应该是m1,m2,m3，实际是{centre_drilling['machine']}"
                print("\n✅ Centre drilling显示和保存功能正常！")
            else:
                print("✗ 没有找到保存的选择")
        
else:
    print("无法找到图片")

print("\n" + "=" * 70)
print("测试完成！")
print("=" * 70)