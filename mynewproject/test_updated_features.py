#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试更新后的机械零件特征识别功能
"""
import os
import sys
import django
from pathlib import Path

# 设置Django环境
project_path = Path(__file__).parent
sys.path.append(str(project_path))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mynewproject.settings')
django.setup()

from imageprocessor.kimi_service import KimiService
from imageprocessor.models import ProcessedImage

def test_updated_kimi_service():
    """测试更新后的KimiService"""
    print("🧪 测试更新后的KimiService...")
    
    # 获取最新的处理图像
    latest_image = ProcessedImage.objects.filter(status='completed').first()
    
    if not latest_image:
        print("❌ 没有找到已处理的图像，请先上传并处理一张图像")
        return
    
    print(f"📁 使用图像ID: {latest_image.id}")
    
    # 创建KimiService实例
    kimi_service = KimiService()
    
    print("🔄 使用更新后的服务重新分析...")
    
    try:
        # 调用更新后的分析功能
        result = kimi_service.analyze_image(
            latest_image.image.file,
            prompt="请分析这张机械零件图像的特征数量"
        )
        
        if result['success']:
            print("✅ 分析成功！")
            print("📋 分析结果:")
            print("-" * 50)
            print(result['result'])
            print("-" * 50)
            
            # 显示特征数量
            if 'features' in result:
                print("\n📊 特征数量统计:")
                print("=" * 30)
                for feature, count in result['features'].items():
                    print(f"{feature}: {count}")
                print(f"\n🔢 总特征数量: {result['total']}")
            
            # 更新数据库记录
            latest_image.result = result['result']
            latest_image.status = 'completed'
            latest_image.save()
            
            print("\n✅ 数据库记录已更新")
            
        else:
            print(f"❌ 分析失败: {result['error']}")
            
    except Exception as e:
        print(f"❌ 测试过程中出错: {e}")
        import traceback
        traceback.print_exc()

def test_feature_extraction():
    """测试特征提取功能"""
    print("\n🧪 测试特征提取功能...")
    
    kimi_service = KimiService()
    
    # 测试文本
    test_text = """
    经过仔细分析，这张机械零件图像显示：
    
    槽特征: 3个
    孔特征: 5个  
    倒角特征: 2个
    肩特征: 1个
    阶特征: 4个
    
    零件整体结构清晰，制造工艺良好。
    """
    
    print("📋 测试文本:")
    print(test_text)
    
    # 提取特征
    features = kimi_service.extract_feature_counts(test_text)
    
    print("\n📊 提取结果:")
    print("=" * 30)
    for feature, count in features.items():
        print(f"{feature}: {count}")
    
    total = sum(features.values())
    print(f"\n🔢 总计: {total}")
    
    # 验证结果
    expected = {'槽特征': 3, '孔特征': 5, '倒角特征': 2, '肩特征': 1, '阶特征': 4}
    if features == expected:
        print("\n✅ 特征提取功能正常")
    else:
        print("\n❌ 特征提取结果与预期不符")
        print(f"预期: {expected}")
        print(f"实际: {features}")

def main():
    """主函数"""
    print("🔧 测试更新后的机械零件特征识别功能")
    print("=" * 60)
    
    # 测试特征提取功能
    test_feature_extraction()
    
    # 测试完整服务
    test_updated_kimi_service()
    
    print("\n✅ 测试完成")

if __name__ == "__main__":
    main()