#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
机械零件特征数量识别工具 - 最终版本
专门用于识别槽特征、孔特征、倒角特征、肩特征、阶特征的数量
"""
import os
import base64
import sys
import io
import re
from openai import OpenAI

# 设置标准输出编码
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

def analyze_mechanical_features_final(image_path):
    """
    分析机械零件的特征数量 - 最终版本
    
    Args:
        image_path: 图片文件路径
        
    Returns:
        dict: 包含各种特征数量的字典
    """
    print("🔧 机械零件特征数量分析工具")
    print("=" * 60)
    
    # 初始化Kimi API客户端
    client = OpenAI(
        api_key="sk-08Y3C0RnJT00tfnsgZEX2DzRZc9HFgKP0SFvGCsv1GQy5Pgt",
        base_url="https://api.moonshot.cn/v1"
    )
    
    # 检查图片文件是否存在
    if not os.path.exists(image_path):
        print(f"❌ 图片文件不存在: {image_path}")
        return None
    
    print(f"📁 分析图片: {os.path.basename(image_path)}")
    
    # 读取图片文件
    with open(image_path, "rb") as f:
        image_data = f.read()
    
    print(f"📊 图片大小: {len(image_data):,} bytes")
    
    # 将图片编码成base64格式
    image_extension = os.path.splitext(image_path)[1].lower()
    if image_extension == '.jpg':
        image_extension = '.jpeg'  # 标准化扩展名
    
    image_url = f"data:image/{image_extension[1:]};base64,{base64.b64encode(image_data).decode('utf-8')}"
    
    print("🎯 Base64编码完成")
    
    # 创建专业的机械工程分析提示词 - 使用中文以获得更好的识别效果
    mechanical_prompt = """
    你是一个专业的机械工程检测员。请仔细分析这张机械零件图像，准确识别并计数以下制造特征：

    🔍 **需要识别的特征类型：**
    1. 槽特征（SLOTS）- 包括所有类型的槽：矩形槽、T型槽、键槽、凹槽等
    2. 孔特征（HOLES）- 包括所有类型的孔：通孔、盲孔、沉头孔、螺纹孔等  
    3. 倒角特征（CHAMFERS）- 包括边缘倒角、棱角倒角、斜面等
    4. 肩特征（SHOULDERS）- 包括轴肩、台阶肩、支撑肩等
    5. 阶特征（STEPS）- 包括高度台阶、平台台阶、阶梯面等

    📏 **计数规则：**
    - 必须提供准确的整数数量
    - 如果某种特征不存在，数量为0
    - 每个特征都要单独计数，不能重复
    - 只计数清晰可见的特征

    📋 **输出格式要求：**
    请严格按照以下格式输出结果：
    槽特征: X个
    孔特征: Y个  
    倒角特征: Z个
    肩特征: A个
    阶特征: B个

    其中X、Y、Z、A、B必须是具体的整数。
    """
    
    print("🔄 正在调用Kimi Vision API进行分析...")
    
    try:
        # 调用Kimi Vision API
        completion = client.chat.completions.create(
            model="kimi-k2.5",
            messages=[
                {
                    "role": "system", 
                    "content": "你是一个精确的机械工程检测专家，专门负责识别和计数机械零件上的制造特征。"
                },
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": mechanical_prompt,
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": image_url,
                                "detail": "high"
                            },
                        },
                    ],
                },
            ],
            max_tokens=800,
            temperature=1
        )
        
        # 获取分析结果
        result = completion.choices[0].message.content
        print("\n✅ API调用成功")
        print("📋 原始分析结果:")
        print("-" * 50)
        print(result)
        print("-" * 50)
        
        # 提取特征数量
        features = extract_feature_counts(result)
        
        print("\n📊 特征数量统计:")
        print("=" * 30)
        for feature, count in features.items():
            print(f"{feature}: {count}")
        
        total_features = sum(features.values())
        print(f"\n🔢 总特征数量: {total_features}")
        
        return {
            'success': True,
            'raw_result': result,
            'features': features,
            'total': total_features
        }
        
    except Exception as e:
        print(f"❌ API调用失败: {e}")
        return {
            'success': False,
            'error': str(e)
        }

def extract_feature_counts(text):
    """
    从分析结果文本中提取特征数量
    
    Args:
        text: API返回的文本
        
    Returns:
        dict: 特征数量字典
    """
    features = {
        '槽特征': 0,
        '孔特征': 0,
        '倒角特征': 0,
        '肩特征': 0,
        '阶特征': 0
    }
    
    # 定义提取模式 - 支持多种格式
    patterns = {
        '槽特征': [
            r'槽特征[:：]\s*(\d+)个?',
            r'槽[:：]\s*(\d+)个?',
            r'SLOTS?[:：]\s*(\d+)',
            r'(\d+)个槽',
        ],
        '孔特征': [
            r'孔特征[:：]\s*(\d+)个?',
            r'孔[:：]\s*(\d+)个?',
            r'HOLES?[:：]\s*(\d+)',
            r'(\d+)个孔',
        ],
        '倒角特征': [
            r'倒角特征[:：]\s*(\d+)个?',
            r'倒角[:：]\s*(\d+)个?',
            r'CHAMFERS?[:：]\s*(\d+)',
            r'(\d+)个倒角',
        ],
        '肩特征': [
            r'肩特征[:：]\s*(\d+)个?',
            r'肩[:：]\s*(\d+)个?',
            r'SHOULDERS?[:：]\s*(\d+)',
            r'(\d+)个肩',
        ],
        '阶特征': [
            r'阶特征[:：]\s*(\d+)个?',
            r'阶[:：]\s*(\d+)个?',
            r'STEPS?[:：]\s*(\d+)',
            r'(\d+)个阶',
        ]
    }
    
    # 提取数量
    for feature, pattern_list in patterns.items():
        for pattern in pattern_list:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                features[feature] = int(match.group(1))
                break
    
    return features

def main():
    """主函数"""
    # 图片路径
    image_path = r"C:\Users\无敌暴龙战士\Desktop\微信图片_20260304151829_116_19.jpg"
    
    # 分析机械特征
    result = analyze_mechanical_features_final(image_path)
    
    if result and result['success']:
        print("\n🎉 机械特征分析完成！")
        print("\n💡 使用说明:")
        print("   - 可以将此代码集成到你的Django项目中")
        print("   - 建议添加更多的错误处理")
        print("   - 可以考虑使用不同的AI模型进行对比")
        print("   - 如果识别不准确，可以尝试调整提示词")
    else:
        print("\n❌ 分析失败，请检查错误信息")

if __name__ == "__main__":
    main()