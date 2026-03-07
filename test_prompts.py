#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试不同的提示词策略来获取特征数量
"""
import os
import base64
import sys
import io
from openai import OpenAI

# 设置标准输出编码
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

def test_different_prompts():
    """测试不同的提示词"""
    print("🔍 测试不同的提示词策略")
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
    
    image_url = f"data:image/jpeg;base64,{base64.b64encode(image_data).decode('utf-8')}"
    
    # 定义不同的提示词
    prompts = [
        {
            "name": "直接计数",
            "text": "请数一下这张图片中的机械特征：槽、孔、倒角、肩、阶。请只回答数字。"
        },
        {
            "name": "结构化输出", 
            "text": "请分析这张机械零件图片，按以下格式输出：\n槽：X个\n孔：Y个\n倒角：Z个\n肩：A个\n阶：B个\n其中X,Y,Z,A,B是具体数字。"
        },
        {
            "name": "工程描述",
            "text": "作为机械工程师，请描述这个零件的主要制造特征，并给出每类特征的数量。"
        },
        {
            "name": "简单识别",
            "text": "这是什么机械零件？能看到哪些制造特征？请给出数量。"
        }
    ]
    
    for i, prompt_info in enumerate(prompts, 1):
        print(f"\n{'='*60}")
        print(f"🧪 测试 {i}: {prompt_info['name']}")
        print(f"提示词: {prompt_info['text']}")
        
        try:
            completion = client.chat.completions.create(
                model="kimi-k2.5",
                messages=[
                    {"role": "system", "content": "你是 Kimi。"},
                    {
                        "role": "user",
                        "content": [
                            {"type": "image_url", "image_url": {"url": image_url}},
                            {"type": "text", "text": prompt_info['text']}
                        ]
                    }
                ],
                max_tokens=300,
                temperature=1
            )
            
            result = completion.choices[0].message.content
            print(f"✅ 响应成功")
            print(f"结果: {repr(result)}")
            print(f"内容: {result}")
            
            # 提取数字
            import re
            numbers = re.findall(r'\d+', result)
            if numbers:
                print(f"🔢 找到的数字: {numbers}")
            
        except Exception as e:
            print(f"❌ 失败: {e}")

def test_with_simple_image():
    """使用简单图片测试"""
    print(f"\n{'='*60}")
    print("🧪 使用简单几何图形测试")
    
    try:
        from PIL import Image, ImageDraw
        
        # 创建一个简单的测试图片
        img = Image.new('RGB', (400, 300), color='white')
        draw = ImageDraw.Draw(img)
        
        # 绘制一些简单的几何图形
        draw.rectangle([50, 50, 150, 150], outline='black', width=3)  # 矩形
        draw.ellipse([200, 50, 300, 150], outline='black', width=3)  # 圆形
        draw.line([50, 200, 150, 250], fill='black', width=3)  # 线条
        
        # 保存为临时文件
        temp_path = "simple_test.jpg"
        img.save(temp_path)
        
        # 读取并编码
        with open(temp_path, "rb") as f:
            image_data = f.read()
        
        image_url = f"data:image/jpeg;base64,{base64.b64encode(image_data).decode('utf-8')}"
        
        client = OpenAI(
            api_key="sk-08Y3C0RnJT00tfnsgZEX2DzRZc9HFgKP0SFvGCsv1GQy5Pgt",
            base_url="https://api.moonshot.cn/v1"
        )
        
        prompt = "请数一下这张图片中有多少个几何图形：矩形、圆形、线条。"
        
        completion = client.chat.completions.create(
            model="kimi-k2.5",
            messages=[
                {"role": "system", "content": "你是 Kimi。"},
                {
                    "role": "user",
                    "content": [
                        {"type": "image_url", "image_url": {"url": image_url}},
                        {"type": "text", "text": prompt}
                    ]
                }
            ],
            max_tokens=200,
            temperature=1
        )
        
        result = completion.choices[0].message.content
        print(f"简单图形测试结果: {result}")
        
        # 清理临时文件
        if os.path.exists(temp_path):
            os.remove(temp_path)
            
    except Exception as e:
        print(f"简单图形测试失败: {e}")

def main():
    """主函数"""
    test_different_prompts()
    test_with_simple_image()
    print("\n✅ 测试完成")

if __name__ == "__main__":
    main()