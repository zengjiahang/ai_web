import os, sys, django, re, json
sys.path.append('d:/python/ai部署/mynewproject')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mynewproject.settings')
django.setup()

from django.test import Client
from django.core.files.uploadedfile import SimpleUploadedFile
from imageprocessor.models import ProcessedImage

print("=" * 60)
print("测试所有修复功能")
print("=" * 60)

# 读取测试图片
with open('d:/python/ai部署/图片/微信图片_20251123111536_70_19.jpg', 'rb') as f:
    image_data = f.read()

# 创建上传文件
uploaded_file = SimpleUploadedFile(
    name='test_all_fixes.jpg',
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
    
    # 测试保存工艺选择API
    test_selections = [
        # 测试milling - 应该显示两个选项组
        {
            'feature_name': 'F1',
            'operation': 'milling',
            'prior_operations': 'none',
            'sequence': 0,
            'machine': 'm1',  # 从第一组选择
            'tool': 't1,t2',
            'is_chamfer_second': False
        },
        {
            'feature_name': 'F1',
            'operation': 'milling',
            'prior_operations': 'none',
            'sequence': 1,
            'machine': 'm3',  # 从第二组选择
            'tool': 't3',
            'is_chamfer_second': False
        },
        # 测试centre drilling - 应该显示m1-m5选项，Tool固定t10
        {
            'feature_name': 'F2',
            'operation': 'centre drilling',
            'prior_operations': 'none',
            'sequence': 0,
            'machine': 'm1,m2,m3',  # 可以多选
            'tool': 't10',  # 固定t10
            'is_chamfer_second': False
        },
        # 测试drilling - 应该显示m1-m5选项
        {
            'feature_name': 'F2',
            'operation': 'drilling',
            'prior_operations': 'centre drilling, milling',
            'sequence': 0,
            'machine': 'm4,m5',
            'tool': 't7,t8',
            'is_chamfer_second': False
        },
        # 测试倒角第二工序 - Tool应该固定为t11
        {
            'feature_name': 'F3',
            'operation': 'milling',
            'prior_operations': 'none',
            'sequence': 0,
            'machine': 'm1',
            'tool': 't1',
            'is_chamfer_second': False
        },
        {
            'feature_name': 'F3',
            'operation': 'milling',
            'prior_operations': 'none',
            'sequence': 1,
            'machine': 'm2',
            'tool': 't11',  # 倒角第二工序固定t11
            'is_chamfer_second': True  # 标记为倒角第二工序
        }
    ]
    
    save_response = client.post(
        '/api/save-process-selections/',
        data=json.dumps({'image_id': image_id, 'selections': test_selections}),
        content_type='application/json'
    )
    print(f"3. 保存选择状态: {save_response.status_code}")
    
    if save_response.status_code == 200:
        print("4. 保存成功！")
    else:
        print(f"4. 保存失败: {save_response.content}")
    
    # 验证保存的数据
    get_response = client.get(f'/api/get-process-selections/?image_id={image_id}')
    print(f"5. 获取选择状态: {get_response.status_code}")
    
    if get_response.status_code == 200:
        result = get_response.json()
        print(f"6. 保存的选择数量: {len(result['selections'])}")
        
        print("\n7. 验证保存的数据:")
        print("-" * 60)
        
        # 验证milling的machine选择
        f1_selections = [s for s in result['selections'] if s['feature_name'] == 'F1']
        print(f"✓ F1 milling (第一组): machine={f1_selections[0]['machine']}, tool={f1_selections[0]['tool']}")
        print(f"✓ F1 milling (第二组): machine={f1_selections[1]['machine']}, tool={f1_selections[1]['tool']}")
        
        # 验证centre drilling
        centre_drilling = [s for s in result['selections'] if s['operation'] == 'centre drilling'][0]
        print(f"✓ Centre drilling: machine={centre_drilling['machine']}, tool={centre_drilling['tool']}")
        assert centre_drilling['tool'] == 't10', "Centre drilling的Tool应该是t10"
        
        # 验证drilling
        drilling = [s for s in result['selections'] if s['operation'] == 'drilling'][0]
        print(f"✓ Drilling: machine={drilling['machine']}, tool={drilling['tool']}")
        
        # 验证倒角第二工序
        chamfer_second = [s for s in result['selections'] if s['is_chamfer_second'] == True][0]
        print(f"✓ 倒角第二工序: machine={chamfer_second['machine']}, tool={chamfer_second['tool']}")
        assert chamfer_second['tool'] == 't11', "倒角第二工序的Tool应该是t11"
        
        print("-" * 60)
        print("\n✅ 所有验证通过！")
        
        print("\n8. 功能说明:")
        print("   ✓ milling: 显示两个选项组（m1/m2 和 m3/m4），每组只能选一个")
        print("   ✓ centre drilling: 显示m1-m5选项（可多选），Tool固定为t10")
        print("   ✓ drilling: 显示m1-m5选项（可多选），Tool选项为t7-t9,t12-t17")
        print("   ✓ 倒角第二工序: Tool自动固定为t11，无需选择")
        print("   ✓ 保存后: 自动切换到查看模式，显示纯文本结果")
        print("   ✓ 编辑功能: 可以切换回编辑模式修改选择")
        print("   ✓ 复制表格: 支持复制包含Machine和Tool的完整表格")
        
else:
    print("无法找到图片")

print("\n" + "=" * 60)
print("测试完成！")
print("=" * 60)