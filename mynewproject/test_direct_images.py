#!/usr/bin/env python3
"""
直接测试文件夹中的两张图片进行AI特征数量识别
"""
import os
import sys
import django
from pathlib import Path
import base64
from openai import OpenAI

# 设置Django环境
project_path = Path(__file__).parent
sys.path.append(str(project_path))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mynewproject.settings')
django.setup()

from django.conf import settings

def test_image_analysis(image_path, image_name):
    """测试单张图片的分析"""
    print(f"\n🖼️ 测试图片: {image_name}")
    print(f"📁 路径: {image_path}")
    
    try:
        # 初始化Kimi API客户端
        client = OpenAI(
            api_key=settings.KIMI_API_KEY,
            base_url="https://api.moonshot.cn/v1"
        )
        
        # 读取并编码图片
        with open(image_path, 'rb') as image_file:
            image_data = image_file.read()
            base64_image = base64.b64encode(image_data).decode('utf-8')
            
        print(f"📊 图片大小: {len(image_data):,} bytes")
        print(f"🎯 Base64编码长度: {len(base64_image):,} 字符")
        
        # 创建超严格的提示词，强制要求数字输出
        strict_prompt = """
你是一个机械工程检测专家。你必须严格按照以下要求分析这张机械零件图像：

🔢 **强制要求 - 必须提供具体数字：**
你必须数出以下特征的准确数量：
1. 槽特征（SLOTS）- 所有类型的槽
2. 孔特征（HOLES）- 所有类型的孔  
3. 倒角特征（CHAMFERS）- 所有倒角
4. 阶特征（STEPS）- 所有台阶

**输出格式（必须严格遵循）：**
SLOTS: [具体数字]
HOLES: [具体数字]
CHAMFERS: [具体数字]
STEPS: [具体数字]

**重要规则：**
- 必须提供准确的整数计数
- 如果某种特征不存在，必须写"0"
- 不允许使用"几个"、"一些"、"多个"等模糊词语
- 不允许给出范围或估计值
- 每个数字必须是具体的整数

请仔细分析图像并严格按照上述格式输出结果。
"""
        
        print("🔄 调用Kimi Vision API...")
        
        # 调用Kimi Vision API
        completion = client.chat.completions.create(
            model="kimi-k2.5",
            messages=[
                {
                    "role": "system", 
                    "content": "你是一个精确的机械工程检测员，专门负责数出机械零件上的具体特征数量。"
                },
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": strict_prompt,
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{base64_image}",
                                "detail": "high"
                            },
                        },
                    ],
                },
            ],
            max_tokens=500,
            temperature=1
        )
        
        result = completion.choices[0].message.content
        print("✅ API调用成功")
        print("📋 分析结果:")
        print("-" * 50)
        print(result)
        print("-" * 50)
        
        # 提取数字
        import re
        features = ['SLOTS', 'HOLES', 'CHAMFERS', 'STEPS']
        extracted_numbers = {}
        
        print("\n🔍 数字提取结果:")
        for feature in features:
            # 更宽松的模式匹配
            patterns = [
                rf'{feature}:\s*(\d+)',
                rf'{feature.lower()}:\s*(\d+)',
                rf'{feature}.*?(\d+)',
            ]
            
            for pattern in patterns:
                match = re.search(pattern, result, re.IGNORECASE)
                if match:
                    extracted_numbers[feature] = int(match.group(1))
                    break
            
            if feature in extracted_numbers:
                print(f"  ✅ {feature}: {extracted_numbers[feature]}")
            else:
                print(f"  ❌ {feature}: 未找到")
        
        if extracted_numbers:
            total = sum(extracted_numbers.values())
            print(f"  📊 总计: {total}")
        
        return result, extracted_numbers
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return None, {}

def main():
    """主函数"""
    print("🔧 AI机械特征数量识别测试工具")
    print("=" * 60)
    
    # 定义测试图片路径
    test_images = [
        ("微信图片_20251123111536_70_19.jpg", "第一张测试图片"),
        ("微信图片_20260304151829_116_19.jpg", "第二张测试图片")
    ]
    
    base_path = Path("c:/Users/无敌暴龙战士/Desktop/python/ai部署/mynewproject/media/uploads/2026/03/04")
    
    results = []
    
    for image_file, description in test_images:
        image_path = base_path / image_file
        
        if image_path.exists():
            print(f"\n{'='*60}")
            print(f"🧪 {description}")
            print(f"📁 文件存在: {image_path}")
            
            result, numbers = test_image_analysis(str(image_path), image_file)
            results.append({
                'image': image_file,
                'description': description,
                'result': result,
                'numbers': numbers
            })
        else:
            print(f"❌ 文件不存在: {image_path}")
    
    # 总结结果
    print(f"\n{'='*60}")
    print("📊 测试结果总结")
    print("=" * 60)
    
    for i, test_result in enumerate(results, 1):
        print(f"\n{i}. {test_result['description']}")
        print(f"   文件: {test_result['image']}")
        
        if test_result['numbers']:
            print("   ✅ 成功提取到数字:")
            for feature, count in test_result['numbers'].items():
                print(f"      {feature}: {count}")
            total = sum(test_result['numbers'].values())
            print(f"      总计: {total}")
        else:
            print("   ❌ 未提取到有效数字")
    
    # 分析整体表现
    successful_extractions = sum(1 for r in results if r['numbers'])
    print(f"\n📈 整体表现:")
    print(f"   测试图片数量: {len(results)}")
    print(f"   成功提取数量: {successful_extractions}")
    print(f"   成功率: {successful_extractions/len(results)*100:.1f}%")
    
    if successful_extractions == 0:
        print("\n⚠️  建议:")
        print("   1. 考虑调整提示词策略")
        print("   2. 可能需要使用不同的AI模型")
        print("   3. 考虑增加图像预处理步骤")
        print("   4. 添加后处理验证逻辑")

if __name__ == "__main__":
    main()