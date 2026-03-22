#!/usr/bin/env python
"""
清空RAG系统数据脚本
"""

import os
import django
import sys

# 设置Django环境
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mynewproject.settings')
django.setup()

from imageprocessor.models import RAGImageFeature, ProcessedImage


def clear_rag_data():
    """清空所有RAG数据"""
    print("🧹 开始清空RAG系统数据...")
    
    # 删除所有RAG特征
    rag_count = RAGImageFeature.objects.count()
    if rag_count > 0:
        RAGImageFeature.objects.all().delete()
        print(f"✅ 已删除 {rag_count} 个RAG特征记录")
    else:
        print("ℹ️  没有找到RAG特征记录")
    
    # 可选：清空所有处理结果（保留图片）
    print("\n是否清空所有AI分析结果？（保留图片文件）")
    response = input("输入 'yes' 清空结果，其他键跳过: ").lower()
    
    if response == 'yes':
        cleared_count = 0
        for image in ProcessedImage.objects.filter(status='completed'):
            image.result = ""
            image.status = 'pending'
            image.processed_at = None
            image.save()
            cleared_count += 1
        print(f"✅ 已清空 {cleared_count} 个处理结果")
    
    print("\n🎉 RAG系统数据清空完成！")
    print("系统已重置，可以开始新的RAG流程。")


if __name__ == '__main__':
    print("⚠️  警告：此操作将清空所有RAG数据！")
    confirm = input("输入 'CLEAR' 确认清空，其他键取消: ")
    
    if confirm == 'CLEAR':
        clear_rag_data()
    else:
        print("操作已取消。")