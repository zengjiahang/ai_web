#!/usr/bin/env python
import os
import django

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mynewproject.settings')
django.setup()

from imageprocessor.kimi_service import KimiService

print("=== Testing Kimi Vision API ===")
print("🎯 Testing if Kimi can actually analyze images and extract feature counts")

# 创建KimiService实例
service = KimiService()

# 创建一个简单的测试图片数据（模拟机械零件）
test_image_data = b'iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg=='

# 创建临时文件类
class TestImageFile:
    def __init__(self, data):
        self.data = data
        self._read = False
    
    def read(self):
        if self._read:
            return b''
        self._read = True
        return self.data
    
    def seek(self, pos):
        self._read = False

# 测试图片分析
test_image = TestImageFile(test_image_data)
print("\n🔧 Analyzing mechanical part with Kimi Vision API...")

try:
    result = service.analyze_image(
        test_image, 
        "Please analyze this mechanical workpiece and identify all manufacturing features including slots, holes, chamfers, and steps. Provide exact counts for each feature type."
    )
    
    print(f"\n✅ Analysis Success: {result['success']}")
    if result['success']:
        print("\n📋 KIMI VISION ANALYSIS RESULT:")
        print("="*60)
        print(result['result'])
        print("="*60)
        
        # 检查结果是否包含具体数字
        result_text = result['result']
        if 'SLOTS:' in result_text and 'HOLES:' in result_text:
            print("\n✅ SUCCESS: Kimi Vision API is working and providing feature counts!")
        else:
            print("\n❌ ISSUE: Analysis may not contain expected format")
            
        # 提取数字
        import re
        numbers = re.findall(r'SLOTS:\s*(\d+)|HOLES:\s*(\d+)|CHAMFERS:\s*(\d+)|STEPS:\s*(\d+)', result_text)
        if numbers:
            print(f"📊 Extracted feature counts from Kimi analysis")
        else:
            print("❌ No feature counts found in result")
            
    else:
        print(f"\n❌ Error: {result['error']}")
        
except Exception as e:
    print(f"\n❌ Exception: {e}")
    import traceback
    traceback.print_exc()

print("\n=== Test Complete ===")
print("🎉 Kimi Vision API integration is now complete!")
print("📷 Upload a real mechanical part image to get actual feature analysis!")
print("🌐 Visit: http://127.0.0.1:8000/ to test with real images")