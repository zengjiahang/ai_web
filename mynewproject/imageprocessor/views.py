from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse, Http404
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.views import View
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.utils import timezone
from .forms import ImageUploadForm
from .models import ProcessedImage, RAGImageFeature, ProcessSelection
from .kimi_service import KimiService
from .image_matcher import ImageMatcher
import json
import os


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
        with open('d:/python/ai部署/debug_upload.log', 'a', encoding='utf-8') as log_file:
            log_file.write(f"\n{'='*50}\n")
            log_file.write(f"POST请求开始\n")
            log_file.write(f"时间: {timezone.now()}\n")
            log_file.write(f"{'='*50}\n")
        
        form = ImageUploadForm(request.POST, request.FILES)
        
        with open('d:/python/ai部署/debug_upload.log', 'a', encoding='utf-8') as log_file:
            log_file.write(f"表单验证: {form.is_valid()}\n")
        
        if form.is_valid():
            processed_image = form.save(commit=False)
            processed_image.status = 'processing'
            processed_image.save()
            
            try:
                # 添加日志
                log_file = open('d:/python/ai部署/debug_upload.log', 'a', encoding='utf-8')
                log_file.write(f"\n{'='*50}\n")
                log_file.write(f"新上传: {processed_image.id}\n")
                log_file.write(f"时间: {processed_image.uploaded_at}\n")
                log_file.write(f"{'='*50}\n")
                
                kimi_service = KimiService(enable_rag=True)
                
                print("=== 开始图像匹配 ===")
                log_file.write("=== 开始图像匹配 ===\n")
                
                # 使用图像匹配算法查找RAG库中的相似图片
                image_matcher = ImageMatcher()
                
                # 获取RAG库中已审核的图片
                approved_rags = RAGImageFeature.objects.filter(
                    approval_status='approved'
                ).select_related('processed_image')
                
                print(f"RAG库中已审核图片数量: {approved_rags.count()}")
                
                # 准备候选图片列表
                candidate_images = []
                for rag in approved_rags:
                    img = rag.processed_image
                    img_path = img.image.path
                    print(f"  候选图片: {img_path}")
                    if os.path.exists(img_path):
                        candidate_images.append((img_path, {
                            'processed_image': img,
                            'rag_feature': rag,
                            'features': rag.feature_vector,
                            'positions': {
                                'slot': rag.slot_positions,
                                'hole': rag.hole_positions,
                                'chamfer': rag.chamfer_positions,
                                'shoulder': rag.shoulder_positions,
                                'step': rag.step_positions
                            }
                        }))
                    else:
                        print(f"  路径不存在!")
                
                print(f"候选图片数量: {len(candidate_images)}")
                
                # 查找最相似的3张图片
                query_image_path = processed_image.image.path
                print(f"查询图片路径: {query_image_path}")
                log_file.write(f"查询图片路径: {query_image_path}\n")
                print(f"候选图片数量: {len(candidate_images)}")
                log_file.write(f"候选图片数量: {len(candidate_images)}\n")
                
                similar_images = image_matcher.find_similar_images_by_image(
                    query_image_path, 
                    candidate_images, 
                    top_k=3
                )
                
                print(f"找到 {len(similar_images)} 张相似图片")
                log_file.write(f"找到 {len(similar_images)} 张相似图片\n")
                for i, similar in enumerate(similar_images, 1):
                    print(f"  相似图片{i}: ID={similar['metadata']['processed_image'].id}, 相似度={similar['similarity']:.2%}")
                    log_file.write(f"  相似图片{i}: ID={similar['metadata']['processed_image'].id}, 相似度={similar['similarity']:.2%}\n")
                
                log_file.close()
                
                # 生成增强提示词
                if similar_images:
                    prompt = """请分析这张机械零件图像，识别所有制造特征。

要求：
1. 准确识别槽特征、孔特征、倒角特征、肩特征、阶特征
2. 提供每个特征的准确数量
3. 描述特征的位置和类型
4. 提供详细的计数依据

## 参考相似零件分析

"""
                    for i, similar in enumerate(similar_images, 1):
                        metadata = similar['metadata']
                        features = metadata['features']
                        positions = metadata['positions']
                        
                        prompt += f"""
### 相似零件 #{i} (相似度: {similar['similarity']:.2%})
- **特征数量**: 槽{features['slot']}个, 孔{features['hole']}个, 倒角{features['chamfer']}个, 肩{features['shoulder']}个, 阶{features['step']}个
- **特征位置描述**:
"""
                        if positions['slot']:
                            prompt += f"  - 槽特征: {positions['slot']}\n"
                        if positions['hole']:
                            prompt += f"  - 孔特征: {positions['hole']}\n"
                        if positions['chamfer']:
                            prompt += f"  - 倒角特征: {positions['chamfer']}\n"
                        if positions['shoulder']:
                            prompt += f"  - 肩特征: {positions['shoulder']}\n"
                        if positions['step']:
                            prompt += f"  - 阶特征: {positions['step']}\n"
                    
                    prompt += "\n请参考以上相似零件的特征位置和描述，分析用户上传的图片，返回表格形式的特征统计结果。"
                else:
                    prompt = "Please analyze this mechanical workpiece and identify all manufacturing features including slots, holes, chamfers, and steps. Provide exact counts for each feature type."
                
                # 调用AI分析
                result = kimi_service.analyze_image(
                    processed_image.image.file,
                    prompt=prompt,
                    use_rag=False
                )
                
                if result and result['success']:
                    # 构建包含特征数量的完整结果
                    feature_counts = result.get('features', {})
                    total_count = result.get('total', 0)
                    
                    full_result = f"{result['result']}\n\n"
                    
                    # 添加RAG信息（如果有）
                    if similar_images:
                        full_result += "🔍 RAG增强分析信息:\n"
                        full_result += "=" * 30 + "\n"
                        full_result += f"参考相似图片数量: {len(similar_images)}\n"
                        if similar_images:
                            full_result += "相似图片详情:\n"
                            for i, similar in enumerate(similar_images, 1):
                                metadata = similar['metadata']
                                features = metadata['features']
                                full_result += f"  {i}. 图片ID: {metadata['processed_image'].id} (相似度: {similar['similarity']:.1%})\n"
                                full_result += f"     特征: 槽{features['slot']} 孔{features['hole']} 倒角{features['chamfer']} 肩{features['shoulder']} 阶{features['step']}\n"
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
                    error_msg = result.get('error', 'Unknown error') if result else 'Analysis failed'
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
        table_rows.append([feature_name, 'milling', 'none'])  # 第二行也是none，通过后台chamferFeatures列表识别
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
            
            # 生成倒角特征列表（用于前端识别）
            chamfer_features = []
            feature_counter = 1
            slot_count = features.get('slot', 0)
            for i in range(slot_count):
                feature_counter += 1
            hole_count = features.get('hole', 0)
            for i in range(hole_count):
                feature_counter += 1
            chamfer_count = features.get('chamfer', 0)
            for i in range(chamfer_count):
                chamfer_features.append(f'F{feature_counter}')
                feature_counter += 1
            shoulder_count = features.get('shoulder', 0)
            for i in range(shoulder_count):
                feature_counter += 1
            step_count = features.get('step', 0)
            for i in range(step_count):
                feature_counter += 1
        except Exception as e:
            print(f"Error extracting features for table: {e}")
            print(f"Result text: {processed_image.result[:200] if processed_image.result else 'None'}")
            table_data = []
            chamfer_features = []
    
    print(f"Final table_data: {table_data}")
    print(f"Chamfer features: {chamfer_features}")
    
    return render(request, 'imageprocessor/result.html', {
        'processed_image': processed_image,
        'table_data': table_data,
        'chamfer_features': chamfer_features
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


@method_decorator(csrf_exempt, name='dispatch')
class SaveProcessSelectionsAPIView(View):
    """保存工艺选择API"""
    
    def post(self, request):
        """保存用户选择的Machine和Tool"""
        try:
            data = json.loads(request.body)
            image_id = data.get('image_id')
            selections = data.get('selections', [])
            
            # 获取图片对象
            processed_image = get_object_or_404(ProcessedImage, id=image_id)
            
            # 删除旧的记录
            ProcessSelection.objects.filter(processed_image=processed_image).delete()
            
            # 为每个特征的不同行分配sequence号
            feature_sequences = {}
            
            # 保存新的选择
            for selection_data in selections:
                feature_name = selection_data.get('feature_name')
                operation = selection_data.get('operation')
                
                # 为每个特征的不同行分配sequence号
                key = f"{feature_name}_{operation}"
                if key not in feature_sequences:
                    feature_sequences[key] = 0
                else:
                    feature_sequences[key] += 1
                
                ProcessSelection.objects.create(
                    processed_image=processed_image,
                    feature_name=feature_name,
                    operation=operation,
                    prior_operations=selection_data.get('prior_operations'),
                    sequence=feature_sequences[key],
                    machine=selection_data.get('machine', ''),
                    tool=selection_data.get('tool', ''),
                    is_chamfer_second=selection_data.get('is_chamfer_second', False)
                )
            
            return JsonResponse({
                'success': True,
                'message': '保存成功'
            })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=400)


@method_decorator(csrf_exempt, name='dispatch')
class GetProcessSelectionsAPIView(View):
    """获取工艺选择API"""
    
    def get(self, request):
        """获取已保存的工艺选择"""
        try:
            image_id = request.GET.get('image_id')
            
            if not image_id:
                return JsonResponse({
                    'success': False,
                    'error': '缺少image_id参数'
                }, status=400)
            
            # 获取图片对象
            processed_image = get_object_or_404(ProcessedImage, id=image_id)
            
            # 获取所有选择
            selections = ProcessSelection.objects.filter(
                processed_image=processed_image
            ).order_by('feature_name', 'sequence', 'operation')
            
            # 序列化为JSON
            selections_data = []
            for selection in selections:
                selections_data.append({
                    'feature_name': selection.feature_name,
                    'operation': selection.operation,
                    'prior_operations': selection.prior_operations,
                    'sequence': selection.sequence,
                    'machine': selection.machine,
                    'tool': selection.tool,
                    'is_chamfer_second': selection.is_chamfer_second
                })
            
            return JsonResponse({
                'success': True,
                'selections': selections_data
            })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=400)