#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试简化版机械零件特征识别功能
"""
import os
import sys
import django
from pathlib import Path

# 设置Django环境
project_path = Path(__file__).parent
sys.path.append(str(project_path))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'simple_ai_analyzer.settings')
django.setup()

from analyzer.views import analyze_image_features

def test_simple_analyzer():
    """测试简化版分析器"""
    print("🔧 测试简化版机械零件特征识别")
    print("=" * 60)
    
    # 使用你的图片进行测试
    image_path = r"C:\Users\无敌暴龙战士\Desktop\微信图片_20260304151829_116_19.jpg"
    
    if not os.path.exists(image_path):
        print(f"❌ 图片文件不存在: {image_path}")
        return
    
    print(f"📁 测试图片: {os.path.basename(image_path)}")
    print(f"📊 文件大小: {os.path.getsize(image_path):,} bytes")
    
    print("\n🔄 开始分析...")
    
    try:
        # 调用分析函数
        result = analyze_image_features(image_path)
        
        if result['success']:
            print("✅ 分析成功！")
            print("\n📋 分析结果:")
            print("-" * 50)
            print(result['result'])
            print("-" * 50)
            
            # 显示特征统计
            if 'features' in result:
                print("\n📊 特征数量统计:")
                print("=" * 30)
                for feature, count in result['features'].items():
                    print(f"{feature}: {count}")
                print(f"\n🔢 总特征数量: {result['total']}")
            
        else:
            print(f"❌ 分析失败: {result['error']}")
            
    except Exception as e:
        print(f"❌ 测试过程中出错: {e}")
        import traceback
        traceback.print_exc()

def main():
    """主函数"""
    test_simple_analyzer()
    print("\n✅ 测试完成")
    print("💡 现在你可以访问 http://127.0.0.1:8001/ 来使用网页界面")

if __name__ == "__main__":
    main()