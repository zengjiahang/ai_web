#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
直接测试Kimi API的特征识别能力
"""
import os
import base64
import sys
import io
from openai import OpenAI

# 设置标准输出编码
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

def test_kimi_api_directly():
    """直接测试Kimi API"""
    print("🔍 直接测试Kimi API特征识别")
    print("=" * 60)
    
    # 初始化Kimi API客户端
    client = OpenAI(
        api_key="sk-08Y3C0RnJT00tfnsgZEX2DzRZc9HFgKP0SFvGCsv1GQy5Pgt",
        base_url="https://api.moonshot.cn/v1"
    )
    
    # 图片路径
    image_path = r"C:\Users\无敌暴龙战士\Desktop\微信图片_20260304151829_116_19.jpg"
    
    if not os.path.exists(image_path):
        print(f"❌ 图片文件不存在: {image_path}")
        return
    
    print(f"📁 测试图片: {os.path.basename(image_path)}")
    
    # 读取图片文件
    with open(image_path, "rb") as f:
        image_data = f.read()
    
    print(f"📊 图片大小: {len(image_data):,} bytes")
    
    # 将图片编码成base64格式
    image_extension = os.path.splitext(image_path)[1].lower()
    if image_extension == '.jpg':
        image_extension = '.jpeg'
    
    image_url = f"data:image/{image_extension[1:]};base64,{base64.b64encode(image_data).decode('utf-8')}"
    
    print("🎯 Base64编码完成")
    
    # 使用你的原始提示词
    prompt = "请帮我分析图片里有几个槽特征，几个倒角特征，几个孔特征，几个阶特征，几个肩特征。"
    
    print(f"📝 提示词: {prompt}")
    print("🔄 正在调用Kimi Vision API...")
    
    try:
        # 调用Kimi Vision API
        completion = client.chat.completions.create(
            model="kimi-k2.5",
            messages=[
                {"role": "system", "content": "你是 Kimi。"},
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image_url",
                            "image_url": {"url": image_url}
                        },
                        {
                            "type": "text",
                            "text": prompt
                        }
                    ]
                }
            ],
            max_tokens=500,
            temperature=1
        )
        
        # 获取分析结果
        result_content = completion.choices[0].message.content
        print("\n✅ API调用成功")
        print("📋 原始响应:")
        print("-" * 50)
        print(repr(result_content))
        print("-" * 50)
        print("📝 格式化内容:")
        print(result_content)
        print("-" * 50)
        
        # 提取数字
        import re
        numbers = re.findall(r'\d+', result_content)
        print(f"🔢 提取到的数字: {numbers}")
        
        # 查找特征关键词
        features = ['槽', '孔', '倒角', '肩', '阶']
        found_features = {}
        
        for feature in features:
            if feature in result_content:
                # 查找附近的数字
                pattern = rf'{feature}[^\d]*(\d+)'
                match = re.search(pattern, result_content)
                if match:
                    found_features[feature] = int(match.group(1))
                else:
                    found_features[feature] = "找到但无数值"
        
        print(f"\n📊 特征分析结果:")
        for feature, count in found_features.items():
            print(f"  {feature}: {count}")
        
        return result_content
        
    except Exception as e:
        print(f"❌ API调用失败: {e}")
        import traceback
        traceback.print_exc()
        return None

def main():
    """主函数"""
    test_kimi_api_directly()
    print("\n✅ 测试完成")

if __name__ == "__main__":
    main()