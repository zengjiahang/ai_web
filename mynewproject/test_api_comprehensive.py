#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试API连接和密钥有效性
"""
import os
import base64
import sys
import io
import requests
from openai import OpenAI

# 设置标准输出编码
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

def test_api_connection():
    """测试API连接"""
    print("🔌 测试API连接...")
    
    try:
        # 测试基础连接
        response = requests.get("https://api.moonshot.cn/v1", timeout=10)
        print(f"✅ API服务器可访问，状态码: {response.status_code}")
        return True
    except Exception as e:
        print(f"❌ API服务器连接失败: {e}")
        return False

def test_api_key():
    """测试API密钥"""
    print("\n🔑 测试API密钥...")
    
    try:
        client = OpenAI(
            api_key="sk-08Y3C0RnJT00tfnsgZEX2DzRZc9HFgKP0SFvGCsv1GQy5Pgt",
            base_url="https://api.moonshot.cn/v1"
        )
        
        # 尝试一个简单的文本对话来测试API密钥
        completion = client.chat.completions.create(
            model="kimi-k2.5",
            messages=[
                {"role": "user", "content": "你好，请回复\"测试成功\""}
            ],
            max_tokens=50,
            temperature=1
        )
        
        result = completion.choices[0].message.content
        print(f"✅ API密钥有效，响应: {result}")
        return True
        
    except Exception as e:
        print(f"❌ API密钥测试失败: {e}")
        return False

def test_with_text_only():
    """仅用文本测试"""
    print("\n📝 测试文本对话...")
    
    try:
        client = OpenAI(
            api_key="sk-08Y3C0RnJT00tfnsgZEX2DzRZc9HFgKP0SFvGCsv1GQy5Pgt",
            base_url="https://api.moonshot.cn/v1"
        )
        
        # 测试机械工程相关的问题
        completion = client.chat.completions.create(
            model="kimi-k2.5",
            messages=[
                {"role": "user", "content": "机械零件中常见的制造特征有哪些？请列举5种。"}
            ],
            max_tokens=200,
            temperature=1
        )
        
        result = completion.choices[0].message.content
        print(f"✅ 文本响应成功")
        print(f"📋 结果: {result}")
        return True
        
    except Exception as e:
        print(f"❌ 文本测试失败: {e}")
        return False

def test_with_sample_image():
    """使用简单图片测试"""
    print("\n🖼️ 测试图片识别能力...")
    
    # 创建一个简单的测试图片（纯色背景）
    try:
        from PIL import Image
        import numpy as np
        
        # 创建一个简单的测试图片
        img_array = np.zeros((100, 100, 3), dtype=np.uint8)
        img_array[:, :] = [255, 0, 0]  # 红色背景
        
        test_img = Image.fromarray(img_array)
        
        # 保存为临时文件
        temp_path = "temp_test_image.jpg"
        test_img.save(temp_path)
        
        # 读取并编码
        with open(temp_path, "rb") as f:
            image_data = f.read()
        
        image_url = f"data:image/jpeg;base64,{base64.b64encode(image_data).decode('utf-8')}"
        
        client = OpenAI(
            api_key="sk-08Y3C0RnJT00tfnsgZEX2DzRZc9HFgKP0SFvGCsv1GQy5Pgt",
            base_url="https://api.moonshot.cn/v1"
        )
        
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
                            "text": "这是什么颜色？",
                        },
                    ],
                },
            ],
            max_tokens=100,
            temperature=1
        )
        
        result = completion.choices[0].message.content
        print(f"✅ 图片测试成功")
        print(f"📋 结果: {result}")
        
        # 清理临时文件
        if os.path.exists(temp_path):
            os.remove(temp_path)
        
        return True
        
    except Exception as e:
        print(f"❌ 图片测试失败: {e}")
        return False

def main():
    """主函数"""
    print("🔍 Kimi API全面测试工具")
    print("=" * 60)
    
    # 测试API连接
    connection_ok = test_api_connection()
    
    if connection_ok:
        # 测试API密钥
        key_ok = test_api_key()
        
        if key_ok:
            # 测试文本对话
            text_ok = test_with_text_only()
            
            if text_ok:
                # 测试图片识别
                image_ok = test_with_sample_image()
                
                if image_ok:
                    print("\n✅ 所有测试通过！API工作正常")
                    print("💡 建议:")
                    print("   1. 确保图片文件格式正确")
                    print("   2. 检查图片内容是否清晰")
                    print("   3. 尝试不同的提示词策略")
                else:
                    print("\n⚠️  图片识别测试失败，但文本功能正常")
            else:
                print("\n❌ 文本对话测试失败")
        else:
            print("\n❌ API密钥无效")
    else:
        print("\n❌ 无法连接到API服务器")

if __name__ == "__main__":
    main()