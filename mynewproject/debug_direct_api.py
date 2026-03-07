#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
直接调试API响应内容
"""
import os
import base64
import sys
import io
from openai import OpenAI

# 设置标准输出编码
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

def debug_api_response_directly(image_path):
    """直接调试API响应"""
    print("🔍 直接调试API响应")
    print("=" * 60)
    
    # 初始化Kimi API客户端
    client = OpenAI(
        api_key="sk-08Y3C0RnJT00tfnsgZEX2DzRZc9HFgKP0SFvGCsv1GQy5Pgt",
        base_url="https://api.moonshot.cn/v1"
    )
    
    # 检查图片文件
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
        image_extension = '.jpeg'
    
    image_url = f"data:image/{image_extension[1:]};base64,{base64.b64encode(image_data).decode('utf-8')}"
    
    print("🎯 Base64编码完成")
    
    # 使用你的原始提示词
    original_prompt = "请帮我分析图片里有几个槽特征，几个倒角特征，几个孔特征，几个阶特征，几个肩特征。"
    
    print(f"📝 使用原始提示词: {original_prompt}")
    
    try:
        # 调用Kimi Vision API - 完全按照你的格式
        completion = client.chat.completions.create(
            model="kimi-k2.5",
            messages=[
                {"role": "system", "content": "你是 Kimi。"},
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": image_url,
                            },
                        },
                        {
                            "type": "text",
                            "text": original_prompt,
                        },
                    ],
                },
            ],
        )
        
        print(f"✅ API调用成功")
        print(f"📊 完整响应对象:")
        print(f"  模型: {completion.model}")
        print(f"  ID: {completion.id}")
        print(f"  创建时间: {completion.created}")
        print(f"  使用token: {completion.usage.total_tokens}")
        print(f"  选择数量: {len(completion.choices)}")
        
        # 获取响应内容
        response_content = completion.choices[0].message.content
        print(f"\n📋 响应内容:")
        print(f"  原始内容: {repr(response_content)}")
        print(f"  显示内容: {response_content}")
        
        # 检查是否有内容
        if response_content and response_content.strip():
            print(f"\n✅ 成功获得响应内容")
            return response_content
        else:
            print(f"\n⚠️  响应内容为空")
            return None
        
    except Exception as e:
        print(f"❌ API调用失败: {e}")
        import traceback
        traceback.print_exc()
        return None

def test_with_simpler_approach(image_path):
    """使用更简单的方法测试"""
    print(f"\n🔧 使用更简单的方法测试...")
    
    client = OpenAI(
        api_key="sk-08Y3C0RnJT00tfnsgZEX2DzRZc9HFgKP0SFvGCsv1GQy5Pgt",
        base_url="https://api.moonshot.cn/v1"
    )
    
    # 读取图片文件
    with open(image_path, "rb") as f:
        image_data = f.read()
    
    image_url = f"data:image/jpeg;base64,{base64.b64encode(image_data).decode('utf-8')}"
    
    # 尝试不同的提示词
    prompts = [
        "这是什么零件？",
        "请描述这个机械零件",
        "这个零件有什么特征？",
        "请数一下这个零件上的孔和槽"
    ]
    
    for i, prompt in enumerate(prompts, 1):
        print(f"\n🔄 测试提示词 {i}: {prompt}")
        
        try:
            completion = client.chat.completions.create(
                model="kimi-k2.5",
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "image_url",
                                "image_url": {"url": image_url},
                            },
                            {
                                "type": "text",
                                "text": prompt,
                            },
                        ],
                    },
                ],
                max_tokens=300
            )
            
            result = completion.choices[0].message.content
            print(f"✅ 结果: {repr(result)}")
            
            if result and result.strip():
                print(f"📝 内容: {result}")
                return result
            
        except Exception as e:
            print(f"❌ 失败: {e}")
    
    return None

def main():
    """主函数"""
    # 图片路径
    image_path = r"C:\Users\无敌暴龙战士\Desktop\微信图片_20260304151829_116_19.jpg"
    
    print("🔍 直接调试API响应")
    print("=" * 60)
    
    # 直接调试API响应
    result = debug_api_response_directly(image_path)
    
    if not result:
        # 尝试更简单的方法
        result = test_with_simpler_approach(image_path)
    
    if result:
        print(f"\n🎉 成功获得分析结果！")
        
        # 尝试提取数字
        import re
        numbers = re.findall(r'\d+', result)
        print(f"🔢 提取到的数字: {numbers}")
        
        # 查找特征关键词
        features = ['槽', '孔', '倒角', '肩', '阶']
        found_features = {}
        
        for feature in features:
            if feature in result:
                # 查找附近的数字
                pattern = rf'{feature}[^\d]*(\d+)'
                match = re.search(pattern, result)
                if match:
                    found_features[feature] = int(match.group(1))
                else:
                    found_features[feature] = "找到但无数值"
        
        print(f"\n📊 特征分析结果:")
        for feature, count in found_features.items():
            print(f"  {feature}: {count}")
        
    else:
        print(f"\n❌ 无法获得有效的API响应")
        print("💡 建议:")
        print("   1. 检查图片文件是否正确")
        print("   2. 尝试使用不同的提示词")
        print("   3. 考虑使用其他AI模型")

if __name__ == "__main__":
    main()