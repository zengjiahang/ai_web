from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse, Http404
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.views import View
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import ImageUploadForm
from .admin_forms import AdminRAGUploadForm
from .models import ProcessedImage, RAGImageFeature
from .kimi_service import KimiService
from .advanced_rag_service import AdvancedRAGService
import json


class UserImageUploadView(View):
    """用户图片上传视图 - 标准用户上传路径"""
    
    def get(self, request):
        """显示用户上传页面"""
        form = ImageUploadForm()
        recent_images = ProcessedImage.objects.filter(status='completed').order_by('-processed_at')[:5]
        
        context = {
            'form': form,
            'recent_images': recent_images,
            'upload_type': 'user',  # 标识为用户上传
        }
        return render(request, 'imageprocessor/user_upload.html', context)
    
    def post(self, request):
        """处理用户图片上传"""
        form = ImageUploadForm(request.POST, request.FILES)
        
        if form.is_valid():
            # 保存图片记录
            processed_image = form.save(commit=False)
            processed_image.status = 'processing'
            processed_image.upload_type = 'user'  # 标记为用户上传
            processed_image.save()
            
            try:
                # 第一步：基础AI分析（不使用RAG）
                kimi_service = KimiService(enable_rag=True)
                
                result = kimi_service.analyze_image(
                    processed_image.image.file,
                    prompt="Please analyze this mechanical workpiece and identify all manufacturing features including slots, holes, chamfers, and steps. Provide exact counts for each feature type.",
                    use_rag=False
                )
                
                # 第二步：如果基础分析成功，进行RAG增强分析
                if result and result['success'] and kimi_service.advanced_rag_service:
                    # 从基础分析结果创建临时RAG特征（待审核状态）
                    rag_service = AdvancedRAGService()
                    rag_feature = rag_service.create_rag_feature_from_ai_result(processed_image)
                    
                    if rag_feature:
                        # 查找相似图片（基于已审核的特征）
                        similar_images = rag_service.find_similar_images_for_new_upload(
                            result.get('features', {})
                        )
                        
                        if similar_images:
                            # 生成RAG增强提示词
                            rag_prompt = rag_service.generate_rag_prompt_with_references(
                                similar_images,
                                "Please analyze this mechanical workpiece and identify all manufacturing features including slots, holes, chamfers, and steps. Provide exact counts for each feature type."
                            )
                            
                            # 使用RAG增强提示词重新分析
                            enhanced_result = kimi_service.analyze_image(
                                processed_image.image.file,
                                prompt=rag_prompt,
                                use_rag=False
                            )
                            
                            if enhanced_result and enhanced_result['success']:
                                # 使用增强结果
                                result = enhanced_result
                                result['rag_similar_images'] = similar_images
                                print(f"✅ 用户上传RAG增强分析完成，参考了 {len(similar_images)} 张相似图片")
                            else:
                                print("⚠️  RAG增强分析失败，使用基础分析结果")
                        else:
                            print("ℹ️  没有找到相似图片，使用基础分析结果")
                    else:
                        print("⚠️  创建RAG特征失败，使用基础分析结果")
                
                if result and result['success']:
                    # 构建包含特征数量的完整结果
                    feature_counts = result.get('features', {})
                    total_count = result.get('total', 0)
                    
                    full_result = f"{result['result']}\n\n"
                    
                    # 添加RAG信息（如果有）
                    if 'rag_similar_images' in result:
                        similar_images = result['rag_similar_images']
                        full_result += "🔍 RAG增强分析信息:\n"
                        full_result += "=" * 30 + "\n"
                        full_result += f"参考相似图片数量: {len(similar_images)}\n"
                        if similar_images:
                            full_result += "相似图片详情:\n"
                            for i, img in enumerate(similar_images, 1):
                                full_result += f"  {i}. 图片ID: {img['processed_image'].id} (相似度: {img['similarity']:.1%})\n"
                                full_result += f"     特征: 槽{img['features']['slot']} 孔{img['features']['hole']} 倒角{img['features']['chamfer']} 肩{img['features']['shoulder']} 阶{img['features']['step']}\n"
                        full_result += "\n"
                    
                    if feature_counts:
                        full_result += "📊 特征数量统计:\n"
                        full_result += "=" * 30 + "\n"
                        for feature, count in feature_counts.items():
                            feature_names = {
                                'slot': '槽特征',
                                'hole': '孔特征',
                                'chamfer': '倒角特征',
                                'shoulder': '肩特征',
                                'step': '阶特征'
                            }
                            full_result += f"{feature_names.get(feature, feature)}: {count}个\n"
                        full_result += f"\n🔢 总特征数量: {total_count}\n"
                    
                    processed_image.result = full_result
                    processed_image.status = 'completed'
                    
                    # 添加RAG标注链接
                    if rag_feature:
                        processed_image.result += f"\n🔧 需要人工审核？点击进行RAG标注: http://127.0.0.1:8000/rag/annotate/{processed_image.id}/\n"
                else:
                    error_msg = result.get('error', 'Unknown error') if result else 'RAG analysis failed'
                    processed_image.result = f"处理失败: {error_msg}"
                    processed_image.status = 'failed'
                
                processed_image.save()
                
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return JsonResponse({
                        'success': True,
                        'result': processed_image.result,
                        'image_url': processed_image.image.url,
                        'status': processed_image.status,
                        'rag_annotation_url': f"/rag/annotate/{processed_image.id}/" if rag_feature else None
                    })
                else:
                    return render(request, 'imageprocessor/result.html', {
                        'processed_image': processed_image
                    })
                    
            except Exception as e:
                processed_image.status = 'failed'
                processed_image.result = f"Processing error: {str(e)}"
                processed_image.save()
                
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return JsonResponse({
                        'success': False,
                        'error': str(e)
                    })
                else:
                    return render(request, 'imageprocessor/upload.html', {
                        'form': form,
                        'error': str(e),
                        'upload_type': 'user'
                    })
        else:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': False,
                    'error': 'Form validation failed',
                    'errors': form.errors
                })
            else:
                return render(request, 'imageprocessor/upload.html', {
                    'form': form,
                    'error': 'Form validation failed',
                    'upload_type': 'user'
                })


@method_decorator(login_required, name='dispatch')
class AdminRAGUploadView(View):
    """管理员RAG上传视图 - 管理员专用上传路径"""
    
    def get(self, request):
        """显示管理员上传页面"""
        form = AdminRAGUploadForm()
        
        # 获取RAG统计信息
        rag_service = AdvancedRAGService()
        stats = rag_service.get_rag_statistics()
        
        context = {
            'form': form,
            'upload_type': 'admin_rag',  # 标识为管理员RAG上传
            'rag_stats': stats,
        }
        return render(request, 'imageprocessor/admin_rag_upload.html', context)
    
    def post(self, request):
        """处理管理员RAG图片上传"""
        form = AdminRAGUploadForm(request.POST, request.FILES)
        
        if form.is_valid():
            try:
                # 保存图片记录
                processed_image = ProcessedImage()
                processed_image.image = form.cleaned_data['image']
                processed_image.status = 'completed'  # 管理员上传直接完成
                processed_image.upload_type = 'admin_rag'
                processed_image.result = f"管理员手动录入的RAG数据\n描述: {form.cleaned_data.get('description', '无')}\n"
                processed_image.save()
                
                # 直接创建RAG特征（管理员手动录入）
                rag_feature = RAGImageFeature()
                rag_feature.processed_image = processed_image
                rag_feature.slot_count = form.cleaned_data['slot_count']
                rag_feature.hole_count = form.cleaned_data['hole_count']
                rag_feature.chamfer_count = form.cleaned_data['chamfer_count']
                rag_feature.shoulder_count = form.cleaned_data['shoulder_count']
                rag_feature.step_count = form.cleaned_data['step_count']
                
                # 设置位置信息
                rag_feature.slot_positions = form.cleaned_data['slot_positions']
                rag_feature.hole_positions = form.cleaned_data['hole_positions']
                rag_feature.chamfer_positions = form.cleaned_data['chamfer_positions']
                rag_feature.shoulder_positions = form.cleaned_data['shoulder_positions']
                rag_feature.step_positions = form.cleaned_data['step_positions']
                
                # 管理员上传直接设置为已审核状态
                rag_feature.approval_status = 'approved'
                rag_feature.reviewed_by = request.user.username
                rag_feature.review_notes = '管理员手动录入的RAG数据'
                rag_feature.save()
                
                # 更新特征向量
                rag_feature.update_feature_vector()
                
                messages.success(request, f'✅ RAG数据录入成功！特征ID: {rag_feature.id}')
                return redirect('imageprocessor:rag_feature_list')  # 直接跳转到特征列表
                
            except Exception as e:
                messages.error(request, f'❌ 数据录入失败: {str(e)}')
                return render(request, 'imageprocessor/admin_rag_upload.html', {
                    'form': form,
                    'error': str(e),
                    'upload_type': 'admin_rag'
                })
        else:
            messages.error(request, '❌ 表单验证失败')
            return render(request, 'imageprocessor/admin_rag_upload.html', {
                'form': form,
                'error': 'Form validation failed',
                'upload_type': 'admin_rag'
            })