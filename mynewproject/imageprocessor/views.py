from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse, Http404
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.views import View
from .forms import ImageUploadForm
from .models import ProcessedImage
from .kimi_service import KimiService
import json


class ImageUploadView(View):
    """Image upload view"""
    
    def get(self, request):
        """Display upload page"""
        form = ImageUploadForm()
        recent_images = ProcessedImage.objects.filter(status='completed').order_by('-processed_at')[:5]
        
        context = {
            'form': form,
            'recent_images': recent_images,
        }
        return render(request, 'imageprocessor/upload.html', context)
    
    def post(self, request):
        """Handle image upload"""
        form = ImageUploadForm(request.POST, request.FILES)
        
        if form.is_valid():
            # Save image record
            processed_image = form.save(commit=False)
            processed_image.status = 'processing'
            processed_image.save()
            
            try:
                # Use Kimi API to analyze mechanical part image
                kimi_service = KimiService()
                result = kimi_service.analyze_image(
                    processed_image.image.file,
                    prompt="Please analyze this mechanical workpiece and identify all manufacturing features including slots, holes, chamfers, and steps. Provide exact counts for each feature type."
                )
                
                if result['success']:
                    # 构建包含特征数量的完整结果
                    feature_counts = result.get('features', {})
                    total_count = result.get('total', 0)
                    
                    full_result = f"{result['result']}\n\n"
                    if feature_counts:
                        full_result += "📊 特征数量统计:\n"
                        full_result += "=" * 30 + "\n"
                        for feature, count in feature_counts.items():
                            full_result += f"{feature}: {count}个\n"
                        full_result += f"\n🔢 总特征数量: {total_count}\n"
                    
                    processed_image.result = full_result
                    processed_image.status = 'completed'
                else:
                    processed_image.result = f"处理失败: {result['error']}"
                    processed_image.status = 'failed'
                
                processed_image.save()
                
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return JsonResponse({
                        'success': True,
                        'result': processed_image.result,
                        'image_url': processed_image.image.url,
                        'status': processed_image.status
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
                        'error': str(e)
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
                    'error': 'Form validation failed'
                })


@method_decorator(csrf_exempt, name='dispatch')
class ImageUploadAPIView(View):
    """Image upload API view (for AJAX requests)"""
    
    def post(self, request):
        """Handle API upload request"""
        form = ImageUploadForm(request.POST, request.FILES)
        
        if form.is_valid():
            processed_image = form.save(commit=False)
            processed_image.status = 'processing'
            processed_image.save()
            
            try:
                kimi_service = KimiService()
                result = kimi_service.analyze_image(
                    processed_image.image.file,
                    prompt="Please analyze this mechanical workpiece and identify all manufacturing features including slots, holes, chamfers, and steps. Provide exact counts for each feature type."
                )
                
                if result['success']:
                    processed_image.result = result['result']
                    processed_image.status = 'completed'
                else:
                    processed_image.result = f"Processing failed: {result['error']}"
                    processed_image.status = 'failed'
                
                processed_image.save()
                
                return JsonResponse({
                    'success': True,
                    'data': {
                        'id': processed_image.id,
                        'result': processed_image.result,
                        'image_url': processed_image.image.url,
                        'status': processed_image.status,
                        'processed_at': processed_image.processed_at.isoformat() if processed_image.processed_at else None
                    }
                })
                
            except Exception as e:
                processed_image.status = 'failed'
                processed_image.result = f"Processing error: {str(e)}"
                processed_image.save()
                
                return JsonResponse({
                    'success': False,
                    'error': str(e)
                })
        else:
            return JsonResponse({
                'success': False,
                'error': 'Form validation failed',
                'errors': form.errors
            })


def result_view(request, image_id):
    """Display processing result"""
    processed_image = get_object_or_404(ProcessedImage, id=image_id)
    return render(request, 'imageprocessor/result.html', {
        'processed_image': processed_image
    })


def history_view(request):
    """Display processing history"""
    images = ProcessedImage.objects.all().order_by('-uploaded_at')
    return render(request, 'imageprocessor/history.html', {
        'images': images
    })