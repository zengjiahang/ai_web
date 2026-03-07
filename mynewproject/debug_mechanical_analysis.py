#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
调试版本的机械零件特征识别工具
"""
import os
import base64
import sys
import io
from openai import OpenAI

# 设置标准输出编码
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

def debug_mechanical_analysis(image_path):
    """调试版本的机械零件特征分析"""
    print("🔍 调试版本 - 机械零件特征数量分析工具")
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
    
    # 尝试不同的提示词策略
    prompts = [
        {
            "name": "简单直接",
            "text": "请帮我数一下这张机械零件图片中有多少个槽、孔、倒角、肩、阶。请直接给出数字。"
        },
        {
            "name": "专业工程",
            "text": "作为机械工程师，请分析这个零件：1.槽特征数量 2.孔特征数量 3.倒角特征数量 4.肩特征数量 5.阶特征数量。请按格式回答：槽X个，孔Y个，倒角Z个，肩A个，阶B个"
        },
        {
            "name": "结构化输出",
            "text": "请识别这张机械零件图像中的制造特征并计数：\n槽特征：?个\n孔特征：?个\n倒角特征：?个\n肩特征：?个\n阶特征：?个\n请将?替换为具体数字。"
        }
    ]
    
    results = {}
    
    for i, prompt_info in enumerate(prompts, 1):
        print(f"\n🔄 测试提示词 {i}: {prompt_info['name']}")
        print(f"提示词: {prompt_info['text']}")
        
        try:
            # 调用Kimi Vision API
            completion = client.chat.completions.create(
                model="kimi-k2.5",
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": image_url,
                                    "detail": "high"
                                },
                            },
                            {
                                "type": "text",
                                "text": prompt_info['text'],
                            },
                        ],
                    },
                ],
                max_tokens=500,
                temperature=1
            )
            
            result = completion.choices[0].message.content
            print(f"✅ 响应成功")
            print(f"📋 结果: {repr(result)}")
            print(f"📝 内容: {result}")
            
            # 提取数字
            import re
            numbers = re.findall(r'\d+', result)
            print(f"🔢 找到的数字: {numbers}")
            
            results[prompt_info['name']] = {
                'result': result,
                'numbers': numbers,
                'success': True
            }
            
        except Exception as e:
            print(f"❌ 失败: {e}")
            results[prompt_info['name']] = {
                'error': str(e),
                'success': False
            }
    
    return results

def test_with_different_models(image_path):
    """测试不同模型"""
    print(f"\n🔧 测试不同模型...")
    
    client = OpenAI(
        api_key="sk-08Y3C0RnJT00tfnsgZEX2DzRZc9HFgKP0SFvGCsv1GQy5Pgt",
        base_url="https://api.moonshot.cn/v1"
    )
    
    # 读取图片
    with open(image_path, "rb") as f:
        image_data = f.read()
    
    image_url = f"data:image/jpeg;base64,{base64.b64encode(image_data).decode('utf-8')}"
    
    models = ["kimi-k2.5", "kimi-latest"]
    
    for model in models:
        print(f"\n🔄 测试模型: {model}")
        try:
            completion = client.chat.completions.create(
                model=model,
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": image_url,
                                    "detail": "high"
                                },
                            },
                            {
                                "type": "text",
                                "text": "这张机械零件有几个孔？",
                            },
                        ],
                    },
                ],
                max_tokens=200,
                temperature=1
            )
            
            result = completion.choices[0].message.content
            print(f"✅ {model} 响应: {result}")
            
        except Exception as e:
            print(f"❌ {model} 失败: {e}")

def main():
    """主函数"""
    # 图片路径
    image_path = r"C:\Users\无敌暴龙战士\Desktop\微信图片_20260304151829_116_19.jpg"
    
    print("🔍 开始调试机械零件特征识别...")
    
    # 调试分析
    results = debug_mechanical_analysis(image_path)
    
    if results:
        print(f"\n📊 调试结果总结:")
        for name, result in results.items():
            if result['success']:
                print(f"  {name}: ✅ 数字: {result['numbers']}")
            else:
                print(f"  {name}: ❌ 失败")
    
    # 测试不同模型
    test_with_different_models(image_path)
    
    print("\n✅ 调试完成")

if __name__ == "__main__":
    main()