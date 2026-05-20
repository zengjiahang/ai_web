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
from .image_matcher import ImageMatcher

from .rag_views import get_rag_machine_tool_stats
import json
import os
import random


def _normalize_table_data(raw_table):
    """
    将前端传来的表格数据统一转为字典格式，兼容 list-of-lists 和 list-of-dicts
    输出格式: [{'feature': 'F1', 'operation': 'milling', 'prior_operations': 'none', 'machine': 'm1', 'tool': 't1'}, ...]
    """
    if not raw_table:
        return []
    normalized = []
    for row in raw_table:
        if isinstance(row, list):
            normalized.append({
                'feature': row[0] if len(row) > 0 else '',
                'operation': row[1] if len(row) > 1 else '',
                'prior_operations': row[2] if len(row) > 2 else 'none',
                'machine': row[3] if len(row) > 3 else '',
                'tool': row[4] if len(row) > 4 else '',
            })
        elif isinstance(row, dict):
            normalized.append({
                'feature': row.get('feature', ''),
                'operation': row.get('operation', ''),
                'prior_operations': row.get('prior_operations', 'none'),
                'machine': row.get('machine', ''),
                'tool': row.get('tool', ''),
            })
    return normalized


def _weighted_pick(candidates, counts_dict):
    """
    根据RAG计数概率加权随机选择，保证多样性

    Args:
        candidates: 候选列表，如 ['m1', 'm2', 'm4', 'm5']
        counts_dict: 计数字典，如 {'m1': 10, 'm2': 8, 'm4': 6}

    Returns:
        按概率随机选中的候选项，若均无计数则返回第一个候选
    """
    weights = [counts_dict.get(c, 0) for c in candidates]
    total = sum(weights)
    if total == 0:
        return candidates[0]
    r = random.random() * total
    cumulative = 0
    for c, w in zip(candidates, weights):
        cumulative += w
        if r <= cumulative:
            return c
    return candidates[-1]


def format_features_to_table(features, rag_stats=None):
    """
    将特征数量格式化为表格形式

    Args:
        features: 特征数量字典 {'slot': 2, 'hole': 4, 'chamfer': 1, 'shoulder': 0, 'step': 1}
                  或 {'槽特征': 2, '孔特征': 4, '倒角特征': 1, '肩特征': 0, '阶特征': 1}
        rag_stats: RAG库统计结果，包含每个工序的 machine_counts 和 tool_counts

    Returns:
        list: 表格行数据，每行包含 [Feature, Operation, Prior operations, Machine, Tool]
    """
    table_rows = []
    feature_counter = 1

    # 支持中英文键名
    slot_count = features.get('slot', 0) or features.get('槽特征', 0)
    hole_count = features.get('hole', 0) or features.get('孔特征', 0)
    chamfer_count = features.get('chamfer', 0) or features.get('倒角特征', 0)
    shoulder_count = features.get('shoulder', 0) or features.get('肩特征', 0)
    step_count = features.get('step', 0) or features.get('阶特征', 0)

    # 获取RAG库各工序的统计计数
    if rag_stats:
        milling_machine_counts = rag_stats.get('milling', {}).get('machine_counts', {})
        milling_tool_counts = rag_stats.get('milling', {}).get('tool_counts', {})
        drilling_machine_counts = rag_stats.get('drilling', {}).get('machine_counts', {})
        drilling_tool_counts = rag_stats.get('drilling', {}).get('tool_counts', {})
        cd_machine_counts = rag_stats.get('centre drilling', {}).get('machine_counts', {})
        cd_tool_counts = rag_stats.get('centre drilling', {}).get('tool_counts', {})
    else:
        milling_machine_counts = {}
        milling_tool_counts = {}
        drilling_machine_counts = {}
        drilling_tool_counts = {}
        cd_machine_counts = {}
        cd_tool_counts = {}

    # 槽特征 - 两行milling
    for i in range(slot_count):
        feature_name = f'F{feature_counter}'
        table_rows.append([
            feature_name, 'milling', 'none',
            _weighted_pick(['m1', 'm2', 'm4', 'm5'], milling_machine_counts),
            _weighted_pick(['t1', 't2', 't3', 't4'], milling_tool_counts)
        ])
        table_rows.append([
            feature_name, 'milling', 'none',
            _weighted_pick(['m1', 'm2', 'm4', 'm5'], milling_machine_counts),
            _weighted_pick(['t5', 't6', 't15'], milling_tool_counts)
        ])
        feature_counter += 1

    # 孔特征 - 三行：centre drilling, drilling, milling
    for i in range(hole_count):
        feature_name = f'F{feature_counter}'
        table_rows.append([
            feature_name, 'centre drilling', 'none',
            _weighted_pick(['m1', 'm2', 'm3', 'm4', 'm5'], cd_machine_counts),
            't10'
        ])
        table_rows.append([
            feature_name, 'drilling', 'none',
            _weighted_pick(['m1', 'm2', 'm3', 'm4', 'm5'], drilling_machine_counts),
            _weighted_pick(['t7', 't8', 't9', 't12', 't13', 't14', 't16', 't17'], drilling_tool_counts)
        ])
        table_rows.append([
            feature_name, 'milling', 'drilling',
            _weighted_pick(['m1', 'm2', 'm4', 'm5'], milling_machine_counts),
            _weighted_pick(['t1', 't2', 't3', 't4'], milling_tool_counts)
        ])
        feature_counter += 1

    # 倒角特征 - 两行milling（不变）
    for i in range(chamfer_count):
        feature_name = f'F{feature_counter}'
        table_rows.append([
            feature_name, 'milling', 'none',
            _weighted_pick(['m1', 'm2', 'm4', 'm5'], milling_machine_counts),
            _weighted_pick(['t1', 't2', 't3', 't4'], milling_tool_counts)
        ])
        table_rows.append([
            feature_name, 'milling', 'none',
            _weighted_pick(['m1', 'm2', 'm4', 'm5'], milling_machine_counts),
            't11'
        ])
        feature_counter += 1

    # 肩特征 - 与槽特征规则一致
    for i in range(shoulder_count):
        feature_name = f'F{feature_counter}'
        table_rows.append([
            feature_name, 'milling', 'none',
            _weighted_pick(['m1', 'm2', 'm4', 'm5'], milling_machine_counts),
            _weighted_pick(['t1', 't2', 't3', 't4'], milling_tool_counts)
        ])
        table_rows.append([
            feature_name, 'milling', 'none',
            _weighted_pick(['m1', 'm2', 'm4', 'm5'], milling_machine_counts),
            _weighted_pick(['t5', 't6', 't15'], milling_tool_counts)
        ])
        feature_counter += 1

    # 阶特征 - 只一行milling
    for i in range(step_count):
        feature_name = f'F{feature_counter}'
        table_rows.append([
            feature_name, 'milling', 'none',
            _weighted_pick(['m1', 'm2', 'm4', 'm5'], milling_machine_counts),
            _weighted_pick(['t1', 't2', 't3', 't4'], milling_tool_counts)
        ])
        feature_counter += 1

    return table_rows


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
                kimi_service = KimiService(enable_rag=True)
                
                # 使用图像匹配算法查找RAG库中的相似图片
                image_matcher = ImageMatcher()
                
                # 获取RAG库中已审核的图片
                approved_rags = RAGImageFeature.objects.filter(
                    approval_status='approved'
                ).select_related('processed_image')
                
                # 准备候选图片列表
                candidate_images = []
                for rag in approved_rags:
                    img = rag.processed_image
                    img_path = img.image.path
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
                
                # 查找最相似的3张图片
                query_image_path = processed_image.image.path
                similar_images = image_matcher.find_similar_images_by_image(
                    query_image_path, 
                    candidate_images, 
                    top_k=3
                )
                
                print(f"找到 {len(similar_images)} 张相似图片")
                
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
                    
                    # 获取RAG库统计
                    rag_stats = get_rag_machine_tool_stats()
                    
                    # 格式化特征为表格（包含机器和刀具）
                    table_data = format_features_to_table(feature_counts, rag_stats)
                    
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
                        'image_id': processed_image.id,
                        'status': processed_image.status
                    })
                else:
                    return render(request, 'imageprocessor/result.html', {
                        'processed_image': processed_image,
                        'table_data': table_data
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


def generate_table_api(request):
    """根据特征数量生成工序表（供管理员录入页调用）"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            features = {
                'slot': data.get('slot_count', 0),
                'hole': data.get('hole_count', 0),
                'chamfer': data.get('chamfer_count', 0),
                'shoulder': data.get('shoulder_count', 0),
                'step': data.get('step_count', 0),
            }
            rag_stats = get_rag_machine_tool_stats()
            table_data = format_features_to_table(features, rag_stats)
            return JsonResponse({'success': True, 'table_data': table_data})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    return JsonResponse({'success': False, 'error': 'POST required'})


class AdminRAGUploadView(View):
    """管理员RAG上传视图 - 管理员专用上传路径"""
    
    def get(self, request):
        """显示管理员上传页面"""
        form = AdminRAGUploadForm()

        context = {
            'form': form,
            'upload_type': 'admin_rag',
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
                
                # 保存工序表格数据（统一转为字典格式）
                feature_table_json = request.POST.get('feature_table_data')
                if feature_table_json:
                    try:
                        raw_table = json.loads(feature_table_json)
                        rag_feature.feature_table = _normalize_table_data(raw_table)
                    except json.JSONDecodeError:
                        pass

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