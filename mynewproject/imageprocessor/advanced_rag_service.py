import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from PIL import Image
from django.conf import settings
from .models import RAGImageFeature, ProcessedImage
import json
import re
from typing import List, Dict, Tuple, Optional


class AdvancedRAGService:
    """高级RAG服务 - 支持手动上传和标注工作流"""
    
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
        self.similarity_threshold = 0.3  # 降低阈值以获得更多匹配
        
        # 最大匹配数量
        self.max_matches = 5
    
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
    
    def create_rag_feature_from_ai_result(self, processed_image: ProcessedImage) -> Optional[RAGImageFeature]:
        """从AI分析结果创建RAG特征（临时状态）"""
        try:
            # 从AI结果中提取特征
            features = self.extract_features_from_result(processed_image.result)
            
            # 创建RAG特征记录（状态为待审核）
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
            
            # 标记为AI自动提取（待审核）
            rag_feature.feature_vector = {
                'source': 'ai_extraction',
                'status': 'pending_review',
                'ai_confidence': 0.8,  # 假设的置信度
                'slot': features.get('slot', 0),
                'hole': features.get('hole', 0),
                'chamfer': features.get('chamfer', 0),
                'shoulder': features.get('shoulder', 0),
                'step': features.get('step', 0),
                'total': sum(features.values())
            }
            rag_feature.save()
            
            return rag_feature
            
        except Exception as e:
            print(f"从AI结果创建RAG特征失败: {e}")
            return None
    
    def find_similar_images_for_new_upload(self, query_features: Dict[str, int]) -> List[Dict]:
        """为新上传的图片查找相似图片（只找已审核的特征）"""
        
        # 获取所有已审核的RAG特征
        candidates = RAGImageFeature.objects.filter(
            feature_vector__status='approved'
        ).select_related('processed_image')
        
        if not candidates.exists():
            # 如果没有已审核的特征，返回空列表
            return []
        
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
        return similarities[:self.max_matches]
    
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
    
    def generate_rag_prompt_with_references(self, similar_images: List[Dict], 
                                          original_prompt: str = None) -> str:
        """生成包含参考信息的RAG提示词"""
        
        if not similar_images:
            # 如果没有相似图片，使用基础提示词
            base_prompt = """你是一个专业的机械工程检测员。请仔细分析这张机械零件图像，准确识别并计数以下制造特征：

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

其中X、Y、Z、A、B必须是具体的整数。"""
            return base_prompt
        
        # 构建包含参考信息的提示词
        rag_prompt = """你是一个专业的机械工程检测员。请仔细分析这张机械零件图像，准确识别并计数以下制造特征。

## 🔍 参考信息（基于相似零件的已审核数据）

基于以下相似零件的已审核特征数据，请参考对比：

"""
        
        for i, similar in enumerate(similar_images, 1):
            rag_prompt += f"""
### 参考零件 #{i} (相似度: {similar['similarity']:.1%})
- **图片ID**: {similar['processed_image'].id}
- **已审核特征数量**: 槽{similar['features']['slot']}个, 孔{similar['features']['hole']}个, 倒角{similar['features']['chamfer']}个, 肩{similar['features']['shoulder']}个, 阶{similar['features']['step']}个
"""
            
            # 添加位置描述信息（如果有已审核的位置标注）
            positions = similar['positions']
            if any(positions.values()):
                rag_prompt += "- **已审核位置描述**:\n"
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
            
            rag_prompt += "\n"
        
        rag_prompt += """
## 📋 当前零件分析要求

请结合以上参考信息，对当前零件进行详细分析：
1. 对比相似零件的特征分布和位置
2. 识别当前零件的独特特征
3. 提供准确的特征计数
4. 描述特征的具体位置和类型
5. 解释与参考零件的异同点

**重要**: 请以当前图像为准进行最终判断，参考信息仅作为对比依据。

📏 **计数规则：**
- 必须提供准确的整数数量
- 如果某种特征不存在，数量为0
- 每个特征都要单独计数，不能重复
- 只计数清晰可见的特征

📊 **输出格式要求：**
请严格按照以下格式输出结果：
槽特征: X个
孔特征: Y个  
倒角特征: Z个
肩特征: A个
阶特征: B个

其中X、Y、Z、A、B必须是具体的整数。"""
        
        return rag_prompt
    
    def approve_rag_feature(self, rag_feature: RAGImageFeature, 
                          approved_features: Dict[str, int],
                          approved_positions: Dict[str, str]) -> RAGImageFeature:
        """审核通过RAG特征"""
        
        # 更新特征数量
        rag_feature.slot_count = approved_features.get('slot', 0)
        rag_feature.hole_count = approved_features.get('hole', 0)
        rag_feature.chamfer_count = approved_features.get('chamfer', 0)
        rag_feature.shoulder_count = approved_features.get('shoulder', 0)
        rag_feature.step_count = approved_features.get('step', 0)
        
        # 更新位置信息
        rag_feature.slot_positions = approved_positions.get('slot', '')
        rag_feature.hole_positions = approved_positions.get('hole', '')
        rag_feature.chamfer_positions = approved_positions.get('chamfer', '')
        rag_feature.shoulder_positions = approved_positions.get('shoulder', '')
        rag_feature.step_positions = approved_positions.get('step', '')
        
        # 更新特征向量（标记为已审核）
        rag_feature.feature_vector = {
            'source': 'manual_approval',
            'status': 'approved',
            'approved_at': str(rag_feature.updated_at),
            'slot': rag_feature.slot_count,
            'hole': rag_feature.hole_count,
            'chamfer': rag_feature.chamfer_count,
            'shoulder': rag_feature.shoulder_count,
            'step': rag_feature.step_count,
            'total': rag_feature.get_total_features()
        }
        
        rag_feature.save()
        return rag_feature
    
    def get_rag_statistics(self) -> Dict:
        """获取RAG系统统计信息"""
        
        total_features = RAGImageFeature.objects.count()
        approved_features = RAGImageFeature.objects.filter(feature_vector__status='approved').count()
        pending_features = RAGImageFeature.objects.filter(feature_vector__status='pending_review').count()
        
        # 特征数量统计
        approved_rags = RAGImageFeature.objects.filter(feature_vector__status='approved')
        
        stats = {
            'total_features': total_features,
            'approved_features': approved_features,
            'pending_features': pending_features,
            'approval_rate': approved_features / total_features * 100 if total_features > 0 else 0,
            'feature_counts': {
                'total_slots': sum(rag.slot_count for rag in approved_rags),
                'total_holes': sum(rag.hole_count for rag in approved_rags),
                'total_chamfers': sum(rag.chamfer_count for rag in approved_rags),
                'total_shoulders': sum(rag.shoulder_count for rag in approved_rags),
                'total_steps': sum(rag.step_count for rag in approved_rags),
            }
        }
        
        return stats