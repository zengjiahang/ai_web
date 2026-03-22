from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.views import View
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from .models import RAGImageFeature
import json


@csrf_exempt
def delete_rag_feature(request, feature_id):
    """删除RAG特征"""
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': '只支持POST请求'})
    
    try:
        feature = get_object_or_404(RAGImageFeature, id=feature_id)
        processed_image = feature.processed_image
        
        # 删除RAG特征
        feature.delete()
        
        # 如果对应的图片没有其他RAG特征，可以选择删除图片记录
        if not RAGImageFeature.objects.filter(processed_image=processed_image).exists():
            processed_image.delete()
        
        return JsonResponse({'success': True, 'message': 'RAG特征删除成功'})
        
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


@csrf_exempt
def bulk_delete_rag_features(request):
    """批量删除RAG特征"""
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': '只支持POST请求'})
    
    try:
        data = json.loads(request.body)
        feature_ids = data.get('feature_ids', [])
        
        if not feature_ids:
            return JsonResponse({'success': False, 'error': '未提供要删除的特征ID'})
        
        deleted_count = 0
        for feature_id in feature_ids:
            try:
                feature = RAGImageFeature.objects.get(id=feature_id)
                processed_image = feature.processed_image
                
                # 删除RAG特征
                feature.delete()
                deleted_count += 1
                
                # 如果对应的图片没有其他RAG特征，可以选择删除图片记录
                if not RAGImageFeature.objects.filter(processed_image=processed_image).exists():
                    processed_image.delete()
                    
            except RAGImageFeature.DoesNotExist:
                continue
        
        return JsonResponse({
            'success': True, 
            'message': f'成功删除 {deleted_count} 个RAG特征',
            'deleted_count': deleted_count
        })
        
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


@csrf_exempt
def edit_rag_feature(request, feature_id):
    """编辑RAG特征"""
    feature = get_object_or_404(RAGImageFeature, id=feature_id)
    
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            
            # 更新特征数量
            feature.slot_count = data.get('slot_count', feature.slot_count)
            feature.hole_count = data.get('hole_count', feature.hole_count)
            feature.chamfer_count = data.get('chamfer_count', feature.chamfer_count)
            feature.shoulder_count = data.get('shoulder_count', feature.shoulder_count)
            feature.step_count = data.get('step_count', feature.step_count)
            
            # 更新位置信息
            feature.slot_positions = data.get('slot_positions', feature.slot_positions)
            feature.hole_positions = data.get('hole_positions', feature.hole_positions)
            feature.chamfer_positions = data.get('chamfer_positions', feature.chamfer_positions)
            feature.shoulder_positions = data.get('shoulder_positions', feature.shoulder_positions)
            feature.step_positions = data.get('step_positions', feature.step_positions)
            
            # 更新审核信息
            if 'approval_status' in data:
                feature.approval_status = data['approval_status']
                feature.reviewed_by = request.user.username
                feature.reviewed_at = timezone.now()
            
            if 'review_notes' in data:
                feature.review_notes = data['review_notes']
            
            feature.save()
            feature.update_feature_vector()
            
            return JsonResponse({
                'success': True, 
                'message': 'RAG特征更新成功',
                'feature': {
                    'id': feature.id,
                    'slot_count': feature.slot_count,
                    'hole_count': feature.hole_count,
                    'chamfer_count': feature.chamfer_count,
                    'shoulder_count': feature.shoulder_count,
                    'step_count': feature.step_count,
                    'approval_status': feature.approval_status,
                    'reviewed_by': feature.reviewed_by,
                    'reviewed_at': str(feature.reviewed_at) if feature.reviewed_at else None
                }
            })
            
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    
    else:
        # GET请求返回特征数据
        return JsonResponse({
            'success': True,
            'feature': {
                'id': feature.id,
                'slot_count': feature.slot_count,
                'hole_count': feature.hole_count,
                'chamfer_count': feature.chamfer_count,
                'shoulder_count': feature.shoulder_count,
                'step_count': feature.step_count,
                'slot_positions': feature.slot_positions,
                'hole_positions': feature.hole_positions,
                'chamfer_positions': feature.chamfer_positions,
                'shoulder_positions': feature.shoulder_positions,
                'step_positions': feature.step_positions,
                'approval_status': feature.approval_status,
                'reviewed_by': feature.reviewed_by,
                'reviewed_at': str(feature.reviewed_at) if feature.reviewed_at else None,
                'review_notes': feature.review_notes,
                'created_at': str(feature.created_at),
                'updated_at': str(feature.updated_at)
            }
        })