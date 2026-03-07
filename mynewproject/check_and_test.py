#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
检查图片文件并尝试基础识别
"""
import os
import base64
import sys
import io
from openai import OpenAI
from PIL import Image

# 设置标准输出编码
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

def check_image_file(image_path):
    """检查图片文件是否有效"""
    print(f"🔍 检查图片文件: {image_path}")
    
    if not os.path.exists(image_path):
        print(f"❌ 文件不存在")
        return False
    
    try:
        # 尝试用PIL打开图片
        with Image.open(image_path) as img:
            print(f"✅ 图片有效")
            print(f"📊 图片信息:")
            print(f"  格式: {img.format}")
            print(f"  尺寸: {img.size}")
            print(f"  模式: {img.mode}")
            return True
    except Exception as e:
        print(f"❌ 图片文件无效: {e}")
        return False

def test_basic_recognition(image_path):
    """测试基础识别功能"""
    print(f"\n🧪 测试基础识别功能...")
    
    # 初始化Kimi API客户端
    client = OpenAI(
        api_key="sk-08Y3C0RnJT00tfnsgZEX2DzRZc9HFgKP0SFvGCsv1GQy5Pgt",
        base_url="https://api.moonshot.cn/v1"
    )
    
    # 读取图片
    with open(image_path, "rb") as f:
        image_data = f.read()
    
    # 编码图片
    image_url = f"data:image/jpeg;base64,{base64.b64encode(image_data).decode('utf-8')}"
    
    # 非常简单的提示词
    simple_prompt = "这是什么？请简单描述。"
    
    print(f"📝 提示词: {simple_prompt}")
    
    try:
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
                            "text": simple_prompt,
                        },
                    ],
                },
            ],
            max_tokens=200,
            temperature=1
        )
        
        result = completion.choices[0].message.content
        print(f"✅ 成功获得响应")
        print(f"📋 结果: {repr(result)}")
        print(f"📝 内容: {result}")
        
        return result
        
    except Exception as e:
        print(f"❌ API调用失败: {e}")
        return None

def test_mechanical_counting(image_path):
    """测试机械特征计数"""
    print(f"\n🔧 测试机械特征计数...")
    
    client = OpenAI(
        api_key="sk-08Y3C0RnJT00tfnsgZEX2DzRZc9HFgKP0SFvGCsv1GQy5Pgt",
        base_url="https://api.moonshot.cn/v1"
    )
    
    # 读取图片
    with open(image_path, "rb") as f:
        image_data = f.read()
    
    image_url = f"data:image/jpeg;base64,{base64.b64encode(image_data).decode('utf-8')}"
    
    # 逐步引导的提示词
    step_prompt = "请按步骤分析：1.这张图片显示的是机械零件吗？2.如果是，请指出主要的制造特征。3.请估计各类特征的数量。"
    
    print(f"📝 提示词: {step_prompt}")
    
    try:
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
                            "text": step_prompt,
                        },
                    ],
                },
            ],
            max_tokens=500,
            temperature=1
        )
        
        result = completion.choices[0].message.content
        print(f"✅ 成功获得响应")
        print(f"📋 结果: {repr(result)}")
        print(f"📝 内容: {result}")
        
        # 尝试提取数字
        import re
        numbers = re.findall(r'\d+', result)
        print(f"🔢 提取到的数字: {numbers}")
        
        return result
        
    except Exception as e:
        print(f"❌ API调用失败: {e}")
        return None

def main():
    """主函数"""
    # 图片路径
    image_path = r"C:\Users\无敌暴龙战士\Desktop\微信图片_20260304151829_116_19.jpg"
    
    print("🔍 开始检查图片和API...")
    print("=" * 60)
    
    # 检查图片文件
    if not check_image_file(image_path):
        print("❌ 图片检查失败，退出程序")
        return
    
    # 测试基础识别
    basic_result = test_basic_recognition(image_path)
    
    if basic_result:
        # 测试机械计数
        mechanical_result = test_mechanical_counting(image_path)
        
        if mechanical_result:
            print("\n✅ 测试完成！看起来API工作正常")
            print("💡 建议:")
            print("   1. 确保提示词清晰明确")
            print("   2. 使用逐步引导的方式")
            print("   3. 考虑图片质量和清晰度")
        else:
            print("\n⚠️  机械特征识别可能需要更精细的提示词")
    else:
        print("\n❌ 基础识别失败，请检查API密钥和网络连接")

if __name__ == "__main__":
    main()