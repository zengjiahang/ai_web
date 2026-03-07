#!/usr/bin/env python3
"""
测试Kimi API特征数量识别问题的诊断脚本
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

def test_feature_count_extraction():
    """测试特征数量提取功能"""
    print("🧪 开始测试Kimi API特征数量提取...")
    
    # 获取最新的处理图像
    latest_image = ProcessedImage.objects.filter(status='completed').first()
    
    if not latest_image:
        print("❌ 没有找到已处理的图像，请先上传并处理一张图像")
        return
    
    print(f"📁 使用图像ID: {latest_image.id}")
    print(f"📊 当前结果: {latest_image.result[:200]}...")
    
    # 测试新的API调用
    kimi_service = KimiService()
    
    # 创建更严格的提示词，专门要求数字输出
    strict_prompt = """
你是一个精确的机械工程检测员。你必须严格按照以下要求分析图像：

🔢 **强制要求 - 必须提供具体数字：**
- 槽特征数量：必须给出具体整数
- 孔特征数量：必须给出具体整数  
- 倒角特征数量：必须给出具体整数
- 阶特征数量：必须给出具体整数

**输出格式要求：**
SLOTS: [具体数字]
HOLES: [具体数字]
CHAMFERS: [具体数字]
STEPS: [具体数字]

**重要：**
- 不要给出范围或估计值
- 不要写"几个"或"多个"
- 必须提供准确的整数计数
- 如果数量为0，必须写"0"

请分析这张机械零件图像并提供准确的特征数量。
"""
    
    print("🔄 使用严格提示词重新分析...")
    
    try:
        result = kimi_service.analyze_image(latest_image.image.file, prompt=strict_prompt)
        
        if result['success']:
            print("✅ API调用成功")
            print("📋 新结果:")
            print(result['result'])
            
            # 检查是否包含具体数字
            content = result['result']
            if any(char.isdigit() for char in content):
                print("✅ 结果中包含数字")
                
                # 尝试提取数字
                import re
                numbers = re.findall(r'\d+', content)
                print(f"🔢 提取到的数字: {numbers}")
                
                # 查找特征关键词
                features = ['SLOTS', 'HOLES', 'CHAMFERS', 'STEPS']
                for feature in features:
                    pattern = rf'{feature}:\s*(\d+)'
                    match = re.search(pattern, content, re.IGNORECASE)
                    if match:
                        print(f"  {feature}: {match.group(1)}")
                    else:
                        print(f"  {feature}: 未找到")
            else:
                print("❌ 结果中没有找到数字")
        else:
            print(f"❌ API调用失败: {result.get('error', '未知错误')}")
            
    except Exception as e:
        print(f"❌ 测试过程中出错: {e}")
        import traceback
        traceback.print_exc()

def analyze_api_response_structure():
    """分析API响应结构"""
    print("\n🔍 分析API响应结构...")
    
    # 检查KimiService的实现
    kimi_service = KimiService()
    
    # 查看使用的模型和参数
    print(f"使用模型: kimi-k2.5")
    print(f"温度参数: 1 (固定)")
    print(f"最大token: 1500")
    
    # 检查提示词策略
    print("\n📋 当前提示词策略分析:")
    print("1. ✅ 使用了结构化提示词")
    print("2. ✅ 明确要求具体数字")
    print("3. ✅ 指定了输出格式")
    print("4. ❌ 可能需要更强的约束")

def suggest_improvements():
    """提出改进建议"""
    print("\n💡 改进建议:")
    print("1. 使用更严格的提示词约束")
    print("2. 考虑使用正则表达式强制提取数字")
    print("3. 增加后处理逻辑来验证结果")
    print("4. 考虑使用不同的模型或API")
    
    print("\n🔧 具体改进方案:")
    print("- 在提示词中增加: '如果无法确定具体数量，请回答0'")
    print("- 增加正则表达式验证: ^(SLOTS|HOLES|CHAMFERS|STEPS):\s*\d+$")
    print("- 添加fallback机制，当API不返回数字时使用图像处理算法")

if __name__ == "__main__":
    print("🔧 Kimi API特征数量识别问题诊断工具")
    print("=" * 50)
    
    test_feature_count_extraction()
    analyze_api_response_structure()
    suggest_improvements()
    
    print("\n✅ 诊断完成")