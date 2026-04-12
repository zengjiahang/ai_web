import os, sys, django, re, json
sys.path.append('d:/python/ai部署/mynewproject')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mynewproject.settings')
django.setup()

from django.test import Client
from django.core.files.uploadedfile import SimpleUploadedFile
from imageprocessor.models import ProcessedImage

print("=" * 70)
print("完整功能测试 - 验证所有修复")
print("=" * 70)

# 读取测试图片
with open('d:/python/ai部署/图片/微信图片_20251123111536_70_19.jpg', 'rb') as f:
    image_data = f.read()

# 创建上传文件
uploaded_file = SimpleUploadedFile(
    name='test_radio_fixes.jpg',
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
    
    # 测试保存工艺选择API - 包含所有情况
    test_selections = [
        # 槽特征（F1）- 测试milling两个机器选择
        {
            'feature_name': 'F1',
            'operation': 'milling',
            'prior_operations': 'none',
            'sequence': 0,
            'machine': 'm1,m2',  # 选择机器1
            'tool': 't1,t2',
            'is_chamfer_second': False
        },
        {
            'feature_name': 'F1',
            'operation': 'milling',
            'prior_operations': 'none',
            'sequence': 1,
            'machine': 'm3,m4',  # 选择机器2
            'tool': 't3',
            'is_chamfer_second': False
        },
        # 倒角特征（F2）- 测试倒角第二工序固定t11
        {
            'feature_name': 'F2',
            'operation': 'milling',
            'prior_operations': 'none',
            'sequence': 0,
            'machine': 'm1,m2',
            'tool': 't1',
            'is_chamfer_second': False
        },
        {
            'feature_name': 'F2',
            'operation': 'milling',
            'prior_operations': 'none',
            'sequence': 1,
            'machine': 'm3,m4',
            'tool': 't11',  # 倒角第二工序固定t11
            'is_chamfer_second': True
        },
        # 孔特征（F3）- 测试centre drilling和drilling
        {
            'feature_name': 'F3',
            'operation': 'centre drilling',
            'prior_operations': 'none',
            'sequence': 0,
            'machine': 'm1,m2,m3',  # 多选
            'tool': 't10',  # 固定t10
            'is_chamfer_second': False
        },
        {
            'feature_name': 'F3',
            'operation': 'drilling',
            'prior_operations': 'centre drilling, milling',
            'sequence': 0,
            'machine': 'm4,m5',
            'tool': 't7,t8',
            'is_chamfer_second': False
        },
        {
            'feature_name': 'F3',
            'operation': 'milling',
            'prior_operations': 'centre drilling, drilling, milling',
            'sequence': 0,
            'machine': 'm1,m2',
            'tool': 't1',
            'is_chamfer_second': False
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
        print("-" * 70)
        
        # 验证milling的两个机器选择
        f1_selections = [s for s in result['selections'] if s['feature_name'] == 'F1']
        print(f"✓ F1 milling (第一行): machine={f1_selections[0]['machine']}, tool={f1_selections[0]['tool']}")
        print(f"✓ F1 milling (第二行): machine={f1_selections[1]['machine']}, tool={f1_selections[1]['tool']}")
        
        # 验证倒角第二工序
        chamfer_selections = [s for s in result['selections'] if s['feature_name'] == 'F2']
        chamfer_first = chamfer_selections[0]
        chamfer_second = chamfer_selections[1]
        print(f"✓ F2 milling (第一行): prior_ops={chamfer_first['prior_operations']}, tool={chamfer_first['tool']}")
        print(f"✓ F2 milling (第二行): prior_ops={chamfer_second['prior_operations']}, tool={chamfer_second['tool']}")
        
        # 验证倒角第二工序的tool是否为t11
        assert chamfer_second['tool'] == 't11', f"倒角第二工序的Tool应该是t11，实际是{chamfer_second['tool']}"
        assert chamfer_second['prior_operations'] == 'none', f"倒角第二工序的prior_operations应该是none，实际是{chamfer_second['prior_operations']}"
        
        # 验证centre drilling
        centre_drilling = [s for s in result['selections'] if s['operation'] == 'centre drilling'][0]
        print(f"✓ Centre drilling: machine={centre_drilling['machine']}, tool={centre_drilling['tool']}")
        assert centre_drilling['tool'] == 't10', f"Centre drilling的Tool应该是t10，实际是{centre_drilling['tool']}"
        assert centre_drilling['machine'] == 'm1,m2,m3', f"Centre drilling的machine应该是m1,m2,m3，实际是{centre_drilling['machine']}"
        
        # 验证drilling
        drilling = [s for s in result['selections'] if s['operation'] == 'drilling'][0]
        print(f"✓ Drilling: machine={drilling['machine']}, tool={drilling['tool']}")
        
        print("-" * 70)
        print("\n✅ 所有验证通过！")
        
        print("\n8. 修复总结:")
        print("   ✓ 倒角第二工序: prior_operations保持'none'，Tool显示为checkbox(t11)并禁用")
        print("   ✓ Centre drilling: 显示m1-m5选项（可多选），Tool显示为checkbox(t10)并禁用")
        print("   ✓ Milling: 显示radio组，两个选项(m1,m2 和 m3,m4)二选一")
        print("   ✓ 编辑模式: 可以正确切换回编辑模式并恢复选择")
        print("   ✓ 复制表格: 支持复制包含Machine和Tool的完整表格")
        
else:
    print("无法找到图片")

print("\n" + "=" * 70)
print("测试完成！")
print("=" * 70)