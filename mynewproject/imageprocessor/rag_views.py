from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.views import View
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from .models import ProcessedImage, RAGImageFeature
from .forms import RAGFeatureAnnotationForm
from .advanced_rag_service import AdvancedRAGService
import json


class RAGReviewView(View):
    """RAG特征审核管理视图"""
    
    def get(self, request):
        """显示待审核列表"""
        # 获取所有待审核的RAG特征
        pending_features = RAGImageFeature.objects.filter(
            approval_status='pending_review'
        ).select_related('processed_image').order_by('-created_at')
        
        # 获取已审核的RAG特征（最近20个）
        reviewed_features = RAGImageFeature.objects.filter(
            approval_status__in=['approved', 'rejected']
        ).select_related('processed_image').order_by('-reviewed_at')[:20]
        
        # 获取统计信息
        rag_service = AdvancedRAGService()
        stats = rag_service.get_rag_statistics()
        
        context = {
            'pending_features': pending_features,
            'reviewed_features': reviewed_features,
            'stats': stats,
        }
        
        return render(request, 'imageprocessor/rag_review.html', context)
    
    def post(self, request):
        """处理审核操作"""
        feature_id = request.POST.get('feature_id')
        action = request.POST.get('action')  # approve or reject
        review_notes = request.POST.get('review_notes', '')
        
        try:
            rag_feature = get_object_or_404(RAGImageFeature, id=feature_id)
            
            if action == 'approve':
                # 获取人工修正的特征数量
                approved_features = {
                    'slot': int(request.POST.get('slot_count', rag_feature.slot_count)),
                    'hole': int(request.POST.get('hole_count', rag_feature.hole_count)),
                    'chamfer': int(request.POST.get('chamfer_count', rag_feature.chamfer_count)),
                    'shoulder': int(request.POST.get('shoulder_count', rag_feature.shoulder_count)),
                    'step': int(request.POST.get('step_count', rag_feature.step_count)),
                }
                
                # 获取人工修正的位置描述
                approved_positions = {
                    'slot': request.POST.get('slot_positions', rag_feature.slot_positions),
                    'hole': request.POST.get('hole_positions', rag_feature.hole_positions),
                    'chamfer': request.POST.get('chamfer_positions', rag_feature.chamfer_positions),
                    'shoulder': request.POST.get('shoulder_positions', rag_feature.shoulder_positions),
                    'step': request.POST.get('step_positions', rag_feature.step_positions),
                }
                
                # 审核通过
                rag_service = AdvancedRAGService()
                rag_service.approve_rag_feature(
                    rag_feature, 
                    approved_features, 
                    approved_positions
                )
                
                messages.success(request, f'✅ 特征 #{feature_id} 审核通过！')
                
            elif action == 'reject':
                # 拒绝特征
                rag_feature.reject_feature(
                    reviewed_by=request.user.username if request.user.is_authenticated else 'admin',
                    review_notes=review_notes
                )
                
                messages.warning(request, f'⚠️ 特征 #{feature_id} 已拒绝')
            
            else:
                messages.error(request, '❌ 无效的操作')
                
        except Exception as e:
            messages.error(request, f'❌ 审核失败: {str(e)}')
        
        return redirect('imageprocessor:rag_review')


def rag_feature_detail(request, feature_id):
    """RAG特征详情页面"""
    rag_feature = get_object_or_404(RAGImageFeature, id=feature_id)
    
    # 查找相似图片（基于已审核的特征）
    rag_service = AdvancedRAGService()
    similar_images = rag_service.find_similar_images_for_new_upload(
        rag_feature.feature_vector
    )
    
    context = {
        'rag_feature': rag_feature,
        'similar_images': similar_images,
        'processed_image': rag_feature.processed_image,
    }
    
    return render(request, 'imageprocessor/rag_feature_detail.html', context)


class RAGAnnotationView(View):
    """RAG特征标注视图（供管理员使用）"""
    
    def get(self, request, image_id):
        """显示标注页面"""
        processed_image = get_object_or_404(ProcessedImage, id=image_id)
        
        # 初始化RAG服务
        rag_service = AdvancedRAGService()
        
        # 获取或创建RAG特征
        try:
            rag_feature = processed_image.rag_features
        except RAGImageFeature.DoesNotExist:
            # 从AI结果中提取特征创建RAG记录
            rag_feature = rag_service.create_rag_feature_from_ai_result(processed_image)
        
        # 创建表单
        form = RAGFeatureAnnotationForm(instance=rag_feature)
        
        # 查找相似图片（基于已审核的特征）
        similar_images = rag_service.find_similar_images_for_new_upload(
            rag_feature.feature_vector
        )
        
        context = {
            'processed_image': processed_image,
            'rag_feature': rag_feature,
            'form': form,
            'feature_vector': rag_feature.feature_vector if rag_feature.feature_vector else {},
            'similar_images': similar_images,
        }
        
        return render(request, 'imageprocessor/rag_annotation.html', context)
    
    def post(self, request, image_id):
        """保存标注数据"""
        processed_image = get_object_or_404(ProcessedImage, id=image_id)
        
        try:
            rag_feature = processed_image.rag_features
        except RAGImageFeature.DoesNotExist:
            return JsonResponse({
                'success': False,
                'error': 'RAG特征不存在'
            })
        
        # 处理表单提交
        form = RAGFeatureAnnotationForm(request.POST, instance=rag_feature)
        
        if form.is_valid():
            rag_feature = form.save()
            
            # 更新特征向量
            rag_feature.update_feature_vector()
            
            messages.success(request, '特征标注已保存！')
            
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': True,
                    'message': '标注已保存',
                    'feature_vector': rag_feature.feature_vector
                })
            else:
                return redirect('imageprocessor:rag_annotation', image_id=image_id)
        else:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': False,
                    'error': '表单验证失败',
                    'errors': form.errors
                })
            else:
                context = {
                    'processed_image': processed_image,
                    'rag_feature': rag_feature,
                    'form': form,
                    'feature_vector': rag_feature.feature_vector if rag_feature.feature_vector else {},
                    'similar_images': [],
                }
                return render(request, 'imageprocessor/rag_annotation.html', context)


def rag_feature_list(request):
    """RAG特征列表页面"""
    # 只显示已审核的特征
    rag_features = RAGImageFeature.objects.filter(
        approval_status='approved'
    ).select_related('processed_image').order_by('-reviewed_at')
    
    # 统计信息
    total_approved = rag_features.count()
    
    # 特征数量统计
    feature_stats = {
        'total_slots': sum(rag.slot_count for rag in rag_features),
        'total_holes': sum(rag.hole_count for rag in rag_features),
        'total_chamfers': sum(rag.chamfer_count for rag in rag_features),
        'total_shoulders': sum(rag.shoulder_count for rag in rag_features),
        'total_steps': sum(rag.step_count for rag in rag_features),
    }
    
    context = {
        'rag_features': rag_features,
        'total_features': total_approved,  # 兼容模板变量名
        'total_approved': total_approved,
        'annotated_features': total_approved,  # 兼容模板变量名
        'feature_stats': feature_stats,
    }
    
    return render(request, 'imageprocessor/rag_feature_list.html', context)