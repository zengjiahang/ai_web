#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
创建测试图片来验证特征识别功能
"""
import os
import sys
import django
from pathlib import Path
from PIL import Image, ImageDraw
import io

# 设置Django环境
project_path = Path(__file__).parent
sys.path.append(str(project_path))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mynewproject.settings')
django.setup()

from imageprocessor.models import ProcessedImage
from imageprocessor.kimi_service import KimiService

def create_test_mechanical_part():
    """创建一个模拟的机械零件图片"""
    print("🔧 创建测试机械零件图片...")
    
    # 创建白色背景图片
    img = Image.new('RGB', (800, 600), color='white')
    draw = ImageDraw.Draw(img)
    
    # 绘制矩形主体
    draw.rectangle([100, 100, 700, 500], outline='black', width=3)
    
    # 绘制孔特征 (4个)
    draw.ellipse([150, 150, 200, 200], outline='black', width=2)  # 孔1
    draw.ellipse([250, 150, 300, 200], outline='black', width=2)  # 孔2
    draw.ellipse([350, 150, 400, 200], outline='black', width=2)  # 孔3
    draw.ellipse([450, 150, 500, 200], outline='black', width=2)  # 孔4
    
    # 绘制槽特征 (2个)
    draw.rectangle([150, 300, 250, 350], outline='black', width=2)  # 槽1
    draw.rectangle([350, 300, 450, 350], outline='black', width=2)  # 槽2
    
    # 绘制倒角特征 (用斜线表示)
    draw.line([100, 100, 130, 130], fill='black', width=2)  # 倒角1
    draw.line([670, 100, 700, 130], fill='black', width=2)  # 倒角2
    
    # 绘制肩特征 (台阶)
    draw.rectangle([100, 400, 300, 500], outline='black', width=3)  # 肩1
    draw.rectangle([500, 400, 700, 500], outline='black', width=3)  # 肩2
    
    # 绘制阶特征 (不同高度)
    draw.line([300, 100, 300, 400], fill='black', width=3)  # 阶1
    draw.line([500, 100, 500, 400], fill='black', width=3)  # 阶2
    
    # 保存图片
    test_image_path = "test_mechanical_part.jpg"
    img.save(test_image_path)
    
    print(f"✅ 测试图片创建完成: {test_image_path}")
    print("📊 预期特征数量:")
    print("  孔特征: 4个")
    print("  槽特征: 2个")
    print("  倒角特征: 2个")
    print("  肩特征: 2个")
    print("  阶特征: 2个")
    
    return test_image_path

def test_with_created_image(image_path):
    """使用创建的测试图片进行分析"""
    print(f"\n🧪 使用创建的测试图片进行分析...")
    
    # 创建KimiService实例
    kimi_service = KimiService()
    
    # 读取图片文件
    with open(image_path, 'rb') as f:
        image_data = f.read()
    
    print(f"📁 图片大小: {len(image_data):,} bytes")
    
    # 创建模拟的Django文件对象
    from django.core.files.base import ContentFile
    image_file = ContentFile(image_data, name="test_mechanical_part.jpg")
    
    print("🔄 开始分析...")
    
    try:
        # 调用分析功能
        result = kimi_service.analyze_image(
            image_file,
            prompt="请分析这个机械零件图像的特征数量"
        )
        
        if result['success']:
            print("✅ 分析成功！")
            print("📋 分析结果:")
            print("-" * 50)
            print(result['result'])
            print("-" * 50)
            
            # 显示特征数量
            if 'features' in result:
                print("\n📊 识别到的特征数量:")
                print("=" * 30)
                for feature, count in result['features'].items():
                    print(f"{feature}: {count}")
                print(f"\n🔢 总特征数量: {result['total']}")
                
                # 对比预期结果
                expected = {
                    '孔特征': 4,
                    '槽特征': 2, 
                    '倒角特征': 2,
                    '肩特征': 2,
                    '阶特征': 2
                }
                
                print("\n📈 对比分析:")
                print("特征类型 | 预期 | 识别 | 准确率")
                print("-" * 35)
                for feature in expected:
                    expected_count = expected[feature]
                    actual_count = result['features'].get(feature, 0)
                    accuracy = "✅" if expected_count == actual_count else "❌"
                    print(f"{feature:8} | {expected_count:4} | {actual_count:4} | {accuracy}")
                
        else:
            print(f"❌ 分析失败: {result['error']}")
            
    except Exception as e:
        print(f"❌ 测试过程中出错: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        # 清理测试文件
        if os.path.exists(image_path):
            os.remove(image_path)
            print(f"\n🗑️  清理测试文件: {image_path}")

def main():
    """主函数"""
    print("🔧 创建测试机械零件图片并验证特征识别")
    print("=" * 60)
    
    # 创建测试图片
    test_image_path = create_test_mechanical_part()
    
    # 使用创建的测试图片进行分析
    test_with_created_image(test_image_path)
    
    print("\n✅ 测试完成")

if __name__ == "__main__":
    main()