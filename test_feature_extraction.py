#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试特征提取函数
"""
import re

def test_feature_extraction():
    """测试特征提取功能"""
    
    # 测试文本1 - 标准格式
    test_text1 = """
    经过仔细分析，这张机械零件图像显示：
    
    槽特征: 3个
    孔特征: 5个  
    倒角特征: 2个
    肩特征: 1个
    阶特征: 4个
    """
    
    # 测试文本2 - Kimi API实际响应格式
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
    
    def extract_features_from_text_v2(text):
        """改进的特征提取函数"""
        features = {
            '槽特征': 0,
            '孔特征': 0,
            '倒角特征': 0,
            '肩特征': 0,
            '阶特征': 0
        }
        
        # 方法1: 直接提取数字（适用于标准格式）
        for feature in features.keys():
            pattern = rf'{feature}[:：]\s*(\d+)个?'
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                features[feature] = int(match.group(1))
        
        # 如果方法1没有找到，尝试方法2: 从**X个**格式中提取
        if all(count == 0 for count in features.values()):
            # 查找**X个**格式
            bold_numbers = re.findall(r'\*\*(\d+)个\*\*', text)
            if len(bold_numbers) >= 5:
                # 假设顺序是：槽、倒角、孔、阶、肩
                features['槽特征'] = int(bold_numbers[0])
                features['倒角特征'] = int(bold_numbers[1])
                features['孔特征'] = int(bold_numbers[2])
                features['阶特征'] = int(bold_numbers[3])
                features['肩特征'] = int(bold_numbers[4])
        
        # 如果还是0，尝试方法3: 从特征名称后的数字提取
        if all(count == 0 for count in features.values()):
            # 槽特征
            slot_match = re.search(r'槽(?:特征)?.*?\*\*(\d+)个\*\*', text, re.IGNORECASE)
            if slot_match:
                features['槽特征'] = int(slot_match.group(1))
            
            # 孔特征
            hole_match = re.search(r'孔(?:特征)?.*?\*\*(\d+)个\*\*', text, re.IGNORECASE)
            if hole_match:
                features['孔特征'] = int(hole_match.group(1))
            
            # 倒角特征
            chamfer_match = re.search(r'倒角(?:特征)?.*?\*\*(\d+)个\*\*', text, re.IGNORECASE)
            if chamfer_match:
                features['倒角特征'] = int(chamfer_match.group(1))
            
            # 肩特征
            shoulder_match = re.search(r'肩(?:特征)?.*?\*\*(\d+)个\*\*', text, re.IGNORECASE)
            if shoulder_match:
                features['肩特征'] = int(shoulder_match.group(1))
            
            # 阶特征
            step_match = re.search(r'阶(?:特征)?.*?\*\*(\d+)个\*\*', text, re.IGNORECASE)
            if step_match:
                features['阶特征'] = int(step_match.group(1))
        
        # 如果还是0，尝试方法4: 从**X个**中提取所有数字
        if all(count == 0 for count in features.values()):
            all_bold_numbers = re.findall(r'\*\*(\d+)个\*\*', text)
            if len(all_bold_numbers) >= 5:
                # 按出现顺序分配
                feature_names = ['槽特征', '倒角特征', '孔特征', '阶特征', '肩特征']
                for i, feature in enumerate(feature_names):
                    if i < len(all_bold_numbers):
                        features[feature] = int(all_bold_numbers[i])
        
        return features
    
    print("🧪 测试特征提取功能")
    print("=" * 60)
    
    print("\n📋 测试文本1 (标准格式):")
    result1 = extract_features_from_text_v2(test_text1)
    print("提取结果:", result1)
    
    print("\n📋 测试文本2 (Kimi API响应格式):")
    result2 = extract_features_from_text_v2(test_text2)
    print("提取结果:", result2)
    
    # 验证结果
    expected1 = {'槽特征': 3, '孔特征': 5, '倒角特征': 2, '肩特征': 1, '阶特征': 4}
    expected2 = {'槽特征': 2, '孔特征': 2, '倒角特征': 0, '肩特征': 0, '阶特征': 1}
    
    print("\n✅ 验证结果:")
    print(f"测试1 - 预期: {expected1}, 实际: {result1}, {'✅ 正确' if result1 == expected1 else '❌ 错误'}")
    print(f"测试2 - 预期: {expected2}, 实际: {result2}, {'✅ 正确' if result2 == expected2 else '❌ 错误'}")
    
    return extract_features_from_text_v2

if __name__ == "__main__":
    extract_function = test_feature_extraction()
    print(f"\n🎯 返回的提取函数: {extract_function.__name__}")