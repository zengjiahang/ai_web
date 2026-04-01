"""
图像匹配服务
使用图像特征进行相似度匹配
"""

import numpy as np
from PIL import Image
import imagehash
from typing import List, Dict, Tuple
from django.core.files.base import File
import os


class ImageMatcher:
    """图像匹配器"""
    
    def __init__(self):
        self.hash_size = 8  # 感知哈希大小
    
    def get_image_hash(self, image_path: str) -> imagehash.ImageHash:
        """获取图像的感知哈希"""
        try:
            img = Image.open(image_path)
            # 使用感知哈希
            return imagehash.phash(img, hash_size=self.hash_size)
        except Exception as e:
            print(f"获取图像哈希失败: {e}")
            return None
    
    def calculate_hash_distance(self, hash1: imagehash.ImageHash, hash2: imagehash.ImageHash) -> int:
        """计算两个哈希之间的汉明距离"""
        if hash1 is None or hash2 is None:
            return float('inf')
        return hash1 - hash2
    
    def calculate_similarity(self, hash1: imagehash.ImageHash, hash2: imagehash.ImageHash) -> float:
        """计算相似度 (0-1)"""
        distance = self.calculate_hash_distance(hash1, hash2)
        max_distance = self.hash_size * self.hash_size
        similarity = 1 - (distance / max_distance)
        return max(0, similarity)
    
    def find_similar_images_by_image(self, query_image_path: str, 
                                   candidate_images: List[Tuple[str, Dict]], 
                                   top_k: int = 3) -> List[Dict]:
        """
        通过图像匹配查找相似图片
        
        Args:
            query_image_path: 查询图片路径
            candidate_images: 候选图片列表 [(image_path, metadata), ...]
            top_k: 返回前k个最相似的
        
        Returns:
            相似图片列表，按相似度降序排列
        """
        query_hash = self.get_image_hash(query_image_path)
        if query_hash is None:
            return []
        
        similarities = []
        
        for img_path, metadata in candidate_images:
            candidate_hash = self.get_image_hash(img_path)
            if candidate_hash is None:
                continue
            
            similarity = self.calculate_similarity(query_hash, candidate_hash)
            
            if similarity > 0:  # 只保留有相似度的
                similarities.append({
                    'image_path': img_path,
                    'metadata': metadata,
                    'similarity': similarity,
                    'hash_distance': self.calculate_hash_distance(query_hash, candidate_hash)
                })
        
        # 按相似度降序排序
        similarities.sort(key=lambda x: x['similarity'], reverse=True)
        
        return similarities[:top_k]