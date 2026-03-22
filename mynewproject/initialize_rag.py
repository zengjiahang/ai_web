#!/usr/bin/env python
"""
RAG系统初始化脚本
为现有的处理图片创建RAG特征记录
"""

import os
import django
import sys

# 设置Django环境
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mynewproject.settings')
django.setup()

from imageprocessor.models import ProcessedImage, RAGImageFeature
from imageprocessor.rag_service import MultimodalRAGService


def initialize_rag_features():
    """为所有已完成的处理图片初始化RAG特征"""
    print("开始初始化RAG特征...")
    
    # 获取所有已完成的处理图片
    completed_images = ProcessedImage.objects.filter(status='completed')
    print(f"找到 {len(completed_images)} 张已完成的处理图片")
    
    rag_service = MultimodalRAGService()
    created_count = 0
    skipped_count = 0
    
    for image in completed_images:
        try:
            # 检查是否已有RAG特征
            if hasattr(image, 'rag_features'):
                print(f"图片 {image.id} 已有RAG特征，跳过")
                skipped_count += 1
                continue
            
            # 从AI分析结果中提取特征
            print(f"正在处理图片 {image.id}...")
            rag_feature = rag_service.create_rag_feature(image)
            
            if rag_feature:
                print(f"✅ 成功创建RAG特征 - 槽:{rag_feature.slot_count}, 孔:{rag_feature.hole_count}, 倒角:{rag_feature.chamfer_count}, 肩:{rag_feature.shoulder_count}, 阶:{rag_feature.step_count}")
                created_count += 1
            else:
                print(f"❌ 创建RAG特征失败 - 图片 {image.id}")
                
        except Exception as e:
            print(f"❌ 处理图片 {image.id} 时出错: {str(e)}")
            continue
    
    print(f"\n初始化完成！")
    print(f"✅ 新创建RAG特征: {created_count} 个")
    print(f"⏭️  跳过已有特征: {skipped_count} 个")
    print(f"📊 RAG特征总数: {RAGImageFeature.objects.count()} 个")


def show_rag_statistics():
    """显示RAG特征统计"""
    print("\n" + "="*50)
    print("RAG特征统计")
    print("="*50)
    
    total_features = RAGImageFeature.objects.count()
    print(f"总RAG特征数量: {total_features}")
    
    if total_features > 0:
        # 特征数量统计
        feature_stats = {
            '槽特征': sum(rag.slot_count for rag in RAGImageFeature.objects.all()),
            '孔特征': sum(rag.hole_count for rag in RAGImageFeature.objects.all()),
            '倒角特征': sum(rag.chamfer_count for rag in RAGImageFeature.objects.all()),
            '肩特征': sum(rag.shoulder_count for rag in RAGImageFeature.objects.all()),
            '阶特征': sum(rag.step_count for rag in RAGImageFeature.objects.all()),
        }
        
        print("\n特征总数统计:")
        for feature, count in feature_stats.items():
            print(f"  {feature}: {count} 个")
        
        # 显示前5个特征的详细信息
        print(f"\n前5个RAG特征详情:")
        for rag in RAGImageFeature.objects.all()[:5]:
            print(f"  图片{rag.processed_image.id}: 槽{rag.slot_count} 孔{rag.hole_count} 倒角{rag.chamfer_count} 肩{rag.shoulder_count} 阶{rag.step_count}")


if __name__ == '__main__':
    print("🚀 启动RAG系统初始化")
    print("="*50)
    
    # 初始化RAG特征
    initialize_rag_features()
    
    # 显示统计信息
    show_rag_statistics()
    
    print("\n✅ RAG系统初始化完成！")
    print("您现在可以使用多模态RAG功能了。")