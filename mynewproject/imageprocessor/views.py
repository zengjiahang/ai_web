from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse, Http404
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.views import View
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from .forms import ImageUploadForm
from .models import ProcessedImage, RAGImageFeature
from .kimi_service import KimiService
from .advanced_rag_service import AdvancedRAGService
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
                # 第一步：基础AI分析（不使用RAG）
                kimi_service = KimiService(enable_rag=True)
                
                # 首先进行基础分析，获取初步特征
                result = kimi_service.analyze_image(
                    processed_image.image.file,
                    prompt="Please analyze this mechanical workpiece and identify all manufacturing features including slots, holes, chamfers, and steps. Provide exact counts for each feature type.",
                    use_rag=False  # 先不使用RAG，等创建RAG特征后再用RAG增强
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
                                use_rag=False  # 已经是增强提示词，不需要内部RAG
                            )
                            
                            if enhanced_result and enhanced_result['success']:
                                # 使用增强结果
                                result = enhanced_result
                                result['rag_similar_images'] = similar_images
                                print(f"✅ RAG增强分析完成，参考了 {len(similar_images)} 张相似图片")
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


def format_features_to_table(features):
    """
    将特征数量格式化为表格形式
    
    Args:
        features: 特征数量字典 {'slot': 2, 'hole': 4, 'chamfer': 1, 'shoulder': 0, 'step': 1}
    
    Returns:
        list: 表格行数据，每行包含 [Feature, Operation, Prior operations]
    """
    table_rows = []
    feature_counter = 1
    
    slot_count = features.get('slot', 0)
    for i in range(slot_count):
        feature_name = f'F{feature_counter}'
        table_rows.append([feature_name, 'milling', 'none'])
        table_rows.append([feature_name, 'milling', 'none'])
        feature_counter += 1
    
    hole_count = features.get('hole', 0)
    for i in range(hole_count):
        feature_name = f'F{feature_counter}'
        PRIOR_ALL = 'centre drilling, drilling, milling'
        PRIOR_TWO = 'centre drilling, milling'
        table_rows.append([feature_name, 'milling', PRIOR_ALL])
        table_rows.append([feature_name, 'drilling', PRIOR_TWO])
        table_rows.append([feature_name, 'centre drilling', 'milling'])
        feature_counter += 1
    
    chamfer_count = features.get('chamfer', 0)
    for i in range(chamfer_count):
        feature_name = f'F{feature_counter}'
        table_rows.append([feature_name, 'milling', 'none'])
        table_rows.append([feature_name, 'milling', 'none'])
        feature_counter += 1
    
    shoulder_count = features.get('shoulder', 0)
    for i in range(shoulder_count):
        feature_name = f'F{feature_counter}'
        table_rows.append([feature_name, 'milling', 'none'])
        table_rows.append([feature_name, 'milling', 'none'])
        feature_counter += 1
    
    step_count = features.get('step', 0)
    for i in range(step_count):
        feature_name = f'F{feature_counter}'
        table_rows.append([feature_name, 'milling', 'none'])
        table_rows.append([feature_name, 'milling', 'none'])
        feature_counter += 1
    
    return table_rows


def result_view(request, image_id):
    """Display processing result"""
    processed_image = get_object_or_404(ProcessedImage, id=image_id)
    
    # 从结果中提取特征数量并格式化为表格
    table_data = []
    if processed_image.status == 'completed' and processed_image.result:
        try:
            # 尝试从结果中提取特征数量 - 使用更灵活的正则表达式
            import re
            
            print(f"========== AI返回的原始内容 ==========")
            print(processed_image.result)
            print(f"======================================")
            
            # 尝试多种可能的格式
            slot_match = re.search(r'槽特征[：:]\s*(\d+)', processed_image.result) or \
                        re.search(r'Slot[：:]\s*(\d+)', processed_image.result) or \
                        re.search(r'槽[：:]\s*(\d+)', processed_image.result)
            
            hole_match = re.search(r'孔特征[：:]\s*(\d+)', processed_image.result) or \
                        re.search(r'Hole[：:]\s*(\d+)', processed_image.result) or \
                        re.search(r'孔[：:]\s*(\d+)', processed_image.result)
            
            chamfer_match = re.search(r'倒角特征[：:]\s*(\d+)', processed_image.result) or \
                            re.search(r'Chamfer[：:]\s*(\d+)', processed_image.result) or \
                            re.search(r'倒角[：:]\s*(\d+)', processed_image.result)
            
            shoulder_match = re.search(r'肩特征[：:]\s*(\d+)', processed_image.result) or \
                         re.search(r'Shoulder[：:]\s*(\d+)', processed_image.result) or \
                         re.search(r'肩[：:]\s*(\d+)', processed_image.result)
            
            step_match = re.search(r'阶特征[：:]\s*(\d+)', processed_image.result) or \
                       re.search(r'Step[：:]\s*(\d+)', processed_image.result) or \
                       re.search(r'阶[：:]\s*(\d+)', processed_image.result)
            
            print(f"Slot match: {slot_match}, Hole match: {hole_match}, Chamfer match: {chamfer_match}")
            print(f"Shoulder match: {shoulder_match}, Step match: {step_match}")
            
            features = {
                'slot': int(slot_match.group(1)) if slot_match else 0,
                'hole': int(hole_match.group(1)) if hole_match else 0,
                'chamfer': int(chamfer_match.group(1)) if chamfer_match else 0,
                'shoulder': int(shoulder_match.group(1)) if shoulder_match else 0,
                'step': int(step_match.group(1)) if step_match else 0
            }
            
            print(f"Extracted features: {features}")
            
            # 格式化为表格
            table_data = format_features_to_table(features)
            print(f"Generated table data with {len(table_data)} rows")
        except Exception as e:
            print(f"Error extracting features for table: {e}")
            print(f"Result text: {processed_image.result[:200] if processed_image.result else 'None'}")
    
    print(f"Final table_data: {table_data}")
    
    return render(request, 'imageprocessor/result.html', {
        'processed_image': processed_image,
        'table_data': table_data
    })


def history_view(request):
    """Display processing history"""
    images = ProcessedImage.objects.all().order_by('-uploaded_at')
    
    paginator = Paginator(images, 10)  # 每页10条
    page = request.GET.get('page', 1)
    
    try:
        images_page = paginator.page(page)
    except PageNotAnInteger:
        images_page = paginator.page(1)
    except EmptyPage:
        images_page = paginator.page(paginator.num_pages)
    
    return render(request, 'imageprocessor/history.html', {
        'images': images_page
    })