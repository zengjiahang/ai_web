from .models import RAGImageFeature, ProcessedImage
import json
import re
from typing import Dict, Optional


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

