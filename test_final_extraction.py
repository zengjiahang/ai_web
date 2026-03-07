#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
最终版本的特征提取函数
"""
import re

def extract_features_final(text):
    """最终版本的特征提取函数"""
    features = {
        '槽特征': 0,
        '孔特征': 0,
        '倒角特征': 0,
        '肩特征': 0,
        '阶特征': 0
    }
    
    print(f"📋 输入文本: {repr(text[:200])}...")
    
    # 方法1: 从表格格式中提取（Kimi API常用格式）
    # 查找 | **特征类型** | **数量** | 格式
    table_rows = re.findall(r'\|\s*\*\*([^|]+)\*\*\s*\|\s*\*\*(\d+)个\*\*\s*\|', text, re.IGNORECASE)
    print(f"📊 找到表格行: {table_rows}")
    
    for row in table_rows:
        feature_name, count = row
        count = int(count)
        
        if '槽' in feature_name:
            features['槽特征'] = count
        elif '孔' in feature_name:
            features['孔特征'] = count
        elif '倒角' in feature_name:
            features['倒角特征'] = count
        elif '肩' in feature_name:
            features['肩特征'] = count
        elif '阶' in feature_name:
            features['阶特征'] = count
    
    # 如果表格方法没有找到，尝试方法2: 从**X个**格式中提取
    if all(count == 0 for count in features.values()):
        bold_numbers = re.findall(r'\*\*(\d+)个\*\*', text)
        print(f"🔢 找到**X个**格式数字: {bold_numbers}")
        
        if len(bold_numbers) >= 5:
            # 按顺序分配（槽、孔、倒角、肩、阶）
            feature_order = ['槽特征', '孔特征', '倒角特征', '肩特征', '阶特征']
            for i, feature in enumerate(feature_order):
                if i < len(bold_numbers):
                    features[feature] = int(bold_numbers[i])
    
    # 如果还是0，尝试方法3: 从标准格式中提取
    if all(count == 0 for count in features.values()):
        for feature in features.keys():
            pattern = rf'{feature}[:：]\s*(\d+)个?'
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                features[feature] = int(match.group(1))
    
    # 如果还是0，尝试方法4: 从"最可能的标准答案"中提取
    if all(count == 0 for count in features.values()):
        final_answer_match = re.search(r'槽\((\d+)\).*?孔\((\d+)\).*?倒角\((\d+)\).*?阶\((\d+)\).*?肩\((\d+)\)', text, re.IGNORECASE)
        if final_answer_match:
            features['槽特征'] = int(final_answer_match.group(1))
            features['孔特征'] = int(final_answer_match.group(2))
            features['倒角特征'] = int(final_answer_match.group(3))
            features['阶特征'] = int(final_answer_match.group(4))
            features['肩特征'] = int(final_answer_match.group(5))
    
    print(f"🎯 提取结果: {features}")
    return features

def test_final_extraction():
    """测试最终提取函数"""
    
    # 测试文本1 - 标准格式
    test_text1 = """
    经过仔细分析，这张机械零件图像显示：
    
    槽特征: 3个
    孔特征: 5个  
    倒角特征: 2个
    肩特征: 1个
    阶特征: 4个
    """
    
    # 测试文本2 - Kimi API实际响应格式（表格格式）
    test_text2 = """根据对这张等轴测工程图的结构分析，各特征数量如下：

## 特征分析
**1. 槽特征 (Slots)：2 个**
- **U形槽**：上部两个立柱之间的半圆形凹槽（连接两侧结构的空腔）
- **矩形槽**：底座前缘（靠近观察者一侧）的缺口/切口，呈矩形凹槽状

**2. 倒角特征 (Chamfers)：0 个**
- 图中所有边缘均为直角相交（90°），没有任何斜切边或倒角线

**3. 孔特征 (Holes)：2 个**
- 底座上有两个圆柱形通孔（虚线显示其贯穿路径和中心线）

**4. 阶特征 (Steps)：1 个**
- 底座前缘的缺口处形成高度差，或底座与上部连接结构之间存在一个台阶过渡（不同高度的平面过渡）

**5. 肩特征 (Shoulders)：0 个**
- 该零件为支架类结构，无轴类零件的轴肩结构；两个圆柱孔为简单通孔，无凸台（Boss）形成的轴肩

---
**注**：如果底座前缘的缺口被视为左右两个独立切口，则槽特征为 **3 个**（1个U形槽+2个矩形缺口）；如果两圆柱孔带有凸台，则肩特征为 **2 个**。但基于当前线框图的简洁表达，以上述保守计数为准。"""
    
    print("🧪 测试最终特征提取函数")
    print("=" * 60)
    
    print("\n📋 测试文本1 (标准格式):")
    result1 = extract_features_final(test_text1)
    expected1 = {'槽特征': 3, '孔特征': 5, '倒角特征': 2, '肩特征': 1, '阶特征': 4}
    print(f"预期: {expected1}")
    print(f"实际: {result1}")
    print(f"结果: {'✅ 正确' if result1 == expected1 else '❌ 错误'}")
    
    print("\n📋 测试文本2 (Kimi API表格格式):")
    result2 = extract_features_final(test_text2)
    expected2 = {'槽特征': 2, '孔特征': 2, '倒角特征': 0, '肩特征': 0, '阶特征': 1}
    print(f"预期: {expected2}")
    print(f"实际: {result2}")
    print(f"结果: {'✅ 正确' if result2 == expected2 else '❌ 错误'}")
    
    return extract_features_final

if __name__ == "__main__":
    extract_function = test_final_extraction()
    print(f"\n🎯 最终提取函数: {extract_function.__name__}")