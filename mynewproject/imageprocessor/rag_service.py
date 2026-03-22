import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from PIL import Image
from django.conf import settings
from .models import RAGImageFeature, ProcessedImage
import json
import re
from typing import List, Dict, Tuple, Optional


class MultimodalRAGService:
    """多模态RAG服务 - 图片+特征描述"""
    
    def __init__(self):
        # 特征权重配置
        self.feature_weights = {
            'slot': 1.0,
            'hole': 1.0,
            'chamfer': 0.8,
            'shoulder': 1.2,
            'step': 1.0
        }
        
        # 相似度阈值
        self.similarity_threshold = 0.6
        
    def extract_features_from_result(self, result_text: str) -> Dict[str, int]:
        """从AI分析结果中提取特征数量"""
        features = {
            'slot': 0,
            'hole': 0,
            'chamfer': 0,
            'shoulder': 0,
            'step': 0
        }
        
        # 使用正则表达式提取特征数量
        patterns = {
            'slot': r'槽(?:特征)?.*?\**(\d+)个\**',
            'hole': r'孔(?:特征)?.*?\**(\d+)个\**',
            'chamfer': r'倒角(?:特征)?.*?\**(\d+)个\**',
            'shoulder': r'肩(?:特征)?.*?\**(\d+)个\**',
            'step': r'阶(?:特征)?.*?\**(\d+)个\**'
        }
        
        for feature, pattern in patterns.items():
            match = re.search(pattern, result_text, re.IGNORECASE)
            if match:
                features[feature] = int(match.group(1))
        
        return features
    
    def create_rag_feature(self, processed_image: ProcessedImage, 
                          manual_features: Optional[Dict[str, int]] = None,
                          manual_positions: Optional[Dict[str, str]] = None) -> RAGImageFeature:
        """创建RAG特征记录"""
        
        # 如果提供了人工标注特征，使用人工标注，否则从AI结果中提取
        if manual_features:
            features = manual_features
        else:
            features = self.extract_features_from_result(processed_image.result)
        
        # 创建RAG特征记录
        rag_feature, created = RAGImageFeature.objects.get_or_create(
            processed_image=processed_image,
            defaults={
                'slot_count': features.get('slot', 0),
                'hole_count': features.get('hole', 0),
                'chamfer_count': features.get('chamfer', 0),
                'shoulder_count': features.get('shoulder', 0),
                'step_count': features.get('step', 0),
            }
        )
        
        # 如果提供了人工标注位置信息
        if manual_positions:
            rag_feature.slot_positions = manual_positions.get('slot', '')
            rag_feature.hole_positions = manual_positions.get('hole', '')
            rag_feature.chamfer_positions = manual_positions.get('chamfer', '')
            rag_feature.shoulder_positions = manual_positions.get('shoulder', '')
            rag_feature.step_positions = manual_positions.get('step', '')
        
        # 更新特征向量
        rag_feature.update_feature_vector()
        
        return rag_feature
    
    def calculate_feature_similarity(self, query_features: Dict[str, int], 
                                   candidate_features: Dict[str, int]) -> float:
        """计算特征相似度"""
        # 转换为向量
        query_vector = np.array([
            query_features.get('slot', 0) * self.feature_weights['slot'],
            query_features.get('hole', 0) * self.feature_weights['hole'],
            query_features.get('chamfer', 0) * self.feature_weights['chamfer'],
            query_features.get('shoulder', 0) * self.feature_weights['shoulder'],
            query_features.get('step', 0) * self.feature_weights['step']
        ]).reshape(1, -1)
        
        candidate_vector = np.array([
            candidate_features.get('slot', 0) * self.feature_weights['slot'],
            candidate_features.get('hole', 0) * self.feature_weights['hole'],
            candidate_features.get('chamfer', 0) * self.feature_weights['chamfer'],
            candidate_features.get('shoulder', 0) * self.feature_weights['shoulder'],
            candidate_features.get('step', 0) * self.feature_weights['step']
        ]).reshape(1, -1)
        
        # 计算余弦相似度
        similarity = cosine_similarity(query_vector, candidate_vector)[0][0]
        return similarity
    
    def find_similar_images(self, query_image: ProcessedImage, top_k: int = 3) -> List[Dict]:
        """找到最相似的图片"""
        
        # 获取查询图片的RAG特征
        try:
            query_rag = query_image.rag_features
            query_features = query_rag.feature_vector
        except RAGImageFeature.DoesNotExist:
            # 如果没有RAG特征，从结果中提取
            query_features = self.extract_features_from_result(query_image.result)
        
        # 获取所有有RAG特征的图片（排除自己）
        candidates = RAGImageFeature.objects.exclude(processed_image=query_image)
        
        similarities = []
        
        for candidate in candidates:
            # 计算相似度
            similarity = self.calculate_feature_similarity(query_features, candidate.feature_vector)
            
            if similarity >= self.similarity_threshold:
                similarities.append({
                    'rag_feature': candidate,
                    'processed_image': candidate.processed_image,
                    'similarity': similarity,
                    'features': candidate.feature_vector,
                    'positions': {
                        'slot': candidate.slot_positions,
                        'hole': candidate.hole_positions,
                        'chamfer': candidate.chamfer_positions,
                        'shoulder': candidate.shoulder_positions,
                        'step': candidate.step_positions
                    }
                })
        
        # 按相似度排序，取前k个
        similarities.sort(key=lambda x: x['similarity'], reverse=True)
        return similarities[:top_k]
    
    def generate_rag_prompt(self, query_image: ProcessedImage, similar_images: List[Dict]) -> str:
        """生成RAG增强的提示词"""
        
        # 基础提示词
        base_prompt = """请分析这张机械零件图像，识别所有制造特征。

要求：
1. 准确识别槽特征、孔特征、倒角特征、肩特征、阶特征
2. 提供每个特征的准确数量
3. 描述特征的位置和类型
4. 提供详细的计数依据

"""
        
        if not similar_images:
            return base_prompt + "\n请基于图像内容进行详细分析。"
        
        # 添加RAG参考信息
        rag_prompt = base_prompt + """
## 参考相似零件分析（RAG增强）

基于以下相似零件的分析结果，请进行参考对比：

"""
        
        for i, similar in enumerate(similar_images, 1):
            rag_prompt += f"""
### 相似零件 #{i} (相似度: {similar['similarity']:.2%})
- **图片ID**: {similar['processed_image'].id}
- **特征数量**: 槽{similar['features']['slot']}个, 孔{similar['features']['hole']}个, 倒角{similar['features']['chamfer']}个, 肩{similar['features']['shoulder']}个, 阶{similar['features']['step']}个
- **特征位置**:
"""
            
            # 添加位置信息（如果有）
            positions = similar['positions']
            if positions['slot']:
                rag_prompt += f"  - 槽特征: {positions['slot']}\n"
            if positions['hole']:
                rag_prompt += f"  - 孔特征: {positions['hole']}\n"
            if positions['chamfer']:
                rag_prompt += f"  - 倒角特征: {positions['chamfer']}\n"
            if positions['shoulder']:
                rag_prompt += f"  - 肩特征: {positions['shoulder']}\n"
            if positions['step']:
                rag_prompt += f"  - 阶特征: {positions['step']}\n"
            
            # 添加原始分析结果的关键信息
            result_preview = similar['processed_image'].result[:200] + "..." if len(similar['processed_image'].result) > 200 else similar['processed_image'].result
            rag_prompt += f"- **分析要点**: {result_preview}\n\n"
        
        rag_prompt += """
## 当前零件分析要求

请结合以上参考信息，对当前零件进行详细分析：
1. 对比相似零件的特征分布
2. 识别当前零件的独特特征
3. 提供准确的特征计数
4. 描述特征的具体位置和类型
5. 解释与参考零件的异同点

**注意**: 请以当前图像为准，参考信息仅作为对比依据。
"""
        
        return rag_prompt
    
    def analyze_with_rag(self, processed_image: ProcessedImage, kimi_service) -> Dict:
        """使用RAG增强进行分析"""
        
        # 1. 确保有RAG特征
        try:
            rag_feature = processed_image.rag_features
        except RAGImageFeature.DoesNotExist:
            # 从AI结果中提取特征创建RAG记录
            rag_feature = self.create_rag_feature(processed_image)
        
        # 2. 找到最相似的图片
        similar_images = self.find_similar_images(processed_image, top_k=3)
        
        # 3. 生成RAG增强提示词
        rag_prompt = self.generate_rag_prompt(processed_image, similar_images)
        
        # 4. 使用RAG提示词进行分析
        result = kimi_service.analyze_image(
            processed_image.image.file,
            prompt=rag_prompt
        )
        
        # 5. 返回结果和RAG信息
        if result['success']:
            result['rag_info'] = {
                'similar_images_count': len(similar_images),
                'similar_images': [
                    {
                        'id': img['processed_image'].id,
                        'similarity': img['similarity'],
                        'features': img['features']
                    } for img in similar_images
                ],
                'rag_prompt_preview': rag_prompt[:200] + '...'
            }
        
        return result