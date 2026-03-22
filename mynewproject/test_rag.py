#!/usr/bin/env python
"""
RAG系统测试脚本
测试多模态RAG功能
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
from imageprocessor.kimi_service import KimiService


def test_rag_similarity_search():
    """测试RAG相似度搜索"""
    print("🧪 测试RAG相似度搜索")
    print("="*50)
    
    # 获取一个测试图片
    test_image = ProcessedImage.objects.filter(status='completed').first()
    if not test_image:
        print("❌ 没有找到已完成的处理图片")
        return
    
    print(f"使用测试图片 ID: {test_image.id}")
    
    # 确保有RAG特征
    try:
        rag_feature = test_image.rag_features
    except RAGImageFeature.DoesNotExist:
        rag_service = MultimodalRAGService()
        rag_feature = rag_service.create_rag_feature(test_image)
        print(f"✅ 创建RAG特征: 槽{rag_feature.slot_count}, 孔{rag_feature.hole_count}, 倒角{rag_feature.chamfer_count}, 肩{rag_feature.shoulder_count}, 阶{rag_feature.step_count}")
    
    # 测试相似度搜索
    rag_service = MultimodalRAGService()
    similar_images = rag_service.find_similar_images(test_image, top_k=3)
    
    print(f"\n找到 {len(similar_images)} 张相似图片:")
    for i, similar in enumerate(similar_images, 1):
        print(f"  {i}. 图片ID: {similar['processed_image'].id} (相似度: {similar['similarity']:.2%})")
        print(f"     特征: 槽{similar['features']['slot']} 孔{similar['features']['hole']} 倒角{similar['features']['chamfer']} 肩{similar['features']['shoulder']} 阶{similar['features']['step']}")
    
    return similar_images


def test_rag_prompt_generation():
    """测试RAG提示词生成"""
    print("\n🧪 测试RAG提示词生成")
    print("="*50)
    
    # 获取测试图片
    test_image = ProcessedImage.objects.filter(status='completed').first()
    if not test_image:
        print("❌ 没有找到已完成的处理图片")
        return
    
    # 获取相似图片
    rag_service = MultimodalRAGService()
    similar_images = rag_service.find_similar_images(test_image, top_k=3)
    
    # 生成RAG提示词
    rag_prompt = rag_service.generate_rag_prompt(test_image, similar_images)
    
    print(f"生成的RAG提示词长度: {len(rag_prompt)} 字符")
    print("提示词预览:")
    print("-" * 30)
    print(rag_prompt[:500] + "..." if len(rag_prompt) > 500 else rag_prompt)
    print("-" * 30)
    
    return rag_prompt


def test_full_rag_analysis():
    """测试完整的RAG增强分析"""
    print("\n🧪 测试完整RAG增强分析")
    print("="*50)
    
    # 获取测试图片
    test_image = ProcessedImage.objects.filter(status='completed').first()
    if not test_image:
        print("❌ 没有找到已完成的处理图片")
        return
    
    print(f"使用测试图片 ID: {test_image.id}")
    
    # 创建RAG服务
    rag_service = MultimodalRAGService()
    kimi_service = KimiService(enable_rag=True)
    
    try:
        # 执行RAG增强分析
        result = rag_service.analyze_with_rag(test_image, kimi_service)
        
        if result and result['success']:
            print("✅ RAG增强分析成功")
            print(f"分析结果长度: {len(result['result'])} 字符")
            
            if 'rag_info' in result:
                rag_info = result['rag_info']
                print(f"参考相似图片: {rag_info['similar_images_count']} 张")
                print("相似图片信息:")
                for img in rag_info['similar_images']:
                    print(f"  - 图片ID: {img['id']} (相似度: {img['similarity']:.2%})")
            
            print("\n分析结果预览:")
            print("-" * 30)
            print(result['result'][:300] + "..." if len(result['result']) > 300 else result['result'])
            print("-" * 30)
            
        else:
            error_msg = result.get('error', 'Unknown error') if result else 'Analysis failed'
            print(f"❌ RAG增强分析失败: {error_msg}")
            
    except Exception as e:
        print(f"❌ 分析过程中出错: {str(e)}")


def show_rag_database_stats():
    """显示RAG数据库统计"""
    print("\n📊 RAG数据库统计")
    print("="*50)
    
    total_rag = RAGImageFeature.objects.count()
    total_processed = ProcessedImage.objects.filter(status='completed').count()
    
    print(f"总处理图片: {total_processed} 张")
    print(f"有RAG特征的图片: {total_rag} 张")
    print(f"RAG覆盖率: {total_rag/total_processed*100:.1f}%")
    
    if total_rag > 0:
        # 特征统计
        stats = {
            '槽特征': sum(rag.slot_count for rag in RAGImageFeature.objects.all()),
            '孔特征': sum(rag.hole_count for rag in RAGImageFeature.objects.all()),
            '倒角特征': sum(rag.chamfer_count for rag in RAGImageFeature.objects.all()),
            '肩特征': sum(rag.shoulder_count for rag in RAGImageFeature.objects.all()),
            '阶特征': sum(rag.step_count for rag in RAGImageFeature.objects.all()),
        }
        
        print(f"\n特征总数统计:")
        for feature, count in stats.items():
            print(f"  {feature}: {count} 个")
        
        # 显示有位置标注的特征数量
        position_stats = {
            '槽位置标注': RAGImageFeature.objects.exclude(slot_positions='').count(),
            '孔位置标注': RAGImageFeature.objects.exclude(hole_positions='').count(),
            '倒角位置标注': RAGImageFeature.objects.exclude(chamfer_positions='').count(),
            '肩位置标注': RAGImageFeature.objects.exclude(shoulder_positions='').count(),
            '阶位置标注': RAGImageFeature.objects.exclude(step_positions='').count(),
        }
        
        print(f"\n位置标注统计:")
        for feature, count in position_stats.items():
            print(f"  {feature}: {count} 个")


if __name__ == '__main__':
    print("🚀 启动RAG系统测试")
    print("="*60)
    
    # 显示数据库统计
    show_rag_database_stats()
    
    # 测试相似度搜索
    similar_images = test_rag_similarity_search()
    
    # 测试提示词生成
    rag_prompt = test_rag_prompt_generation()
    
    # 测试完整RAG分析（可选，因为需要调用API）
    print(f"\n是否测试完整RAG增强分析？(需要消耗API调用)")
    response = input("输入 'y' 继续，其他键跳过: ").lower()
    if response == 'y':
        test_full_rag_analysis()
    
    print("\n✅ RAG系统测试完成！")