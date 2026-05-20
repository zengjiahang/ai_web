from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.views import View
from django.contrib import messages
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from .models import ProcessedImage, RAGImageFeature
from .forms import RAGFeatureAnnotationForm
from .advanced_rag_service import AdvancedRAGService
import json



def rag_feature_detail(request, feature_id):
    """RAG特征详情页面"""
    rag_feature = get_object_or_404(RAGImageFeature, id=feature_id)

    context = {
        'rag_feature': rag_feature,
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
        
        context = {
            'processed_image': processed_image,
            'rag_feature': rag_feature,
            'form': form,
            'feature_vector': rag_feature.feature_vector if rag_feature.feature_vector else {},
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
            
            # 保存表格数据
            feature_table_data = request.POST.get('feature_table')
            if feature_table_data:
                try:
                    feature_table = json.loads(feature_table_data)
                    rag_feature.feature_table = feature_table
                except json.JSONDecodeError:
                    pass
            
            rag_feature.save()
            
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
    
    # 分页处理
    paginator = Paginator(rag_features, 10)  # 每页10条
    page = request.GET.get('page', 1)
    
    try:
        rag_features_page = paginator.page(page)
    except PageNotAnInteger:
        rag_features_page = paginator.page(1)
    except EmptyPage:
        rag_features_page = paginator.page(paginator.num_pages)
    
    # 统计信息（基于所有已审核特征）
    all_approved = RAGImageFeature.objects.filter(approval_status='approved')
    feature_stats = {
        'total_slots': sum(rag.slot_count for rag in all_approved),
        'total_holes': sum(rag.hole_count for rag in all_approved),
        'total_chamfers': sum(rag.chamfer_count for rag in all_approved),
        'total_shoulders': sum(rag.shoulder_count for rag in all_approved),
        'total_steps': sum(rag.step_count for rag in all_approved),
    }
    
    context = {
        'rag_features': rag_features_page,
        'total_features': all_approved.count(),
        'total_approved': all_approved.count(),
        'annotated_features': all_approved.count(),
        'feature_stats': feature_stats,
        'feature_table_data': {rag.id: rag.feature_table for rag in rag_features_page if rag.feature_table}
    }
    
    return render(request, 'imageprocessor/rag_feature_list.html', context)


def get_rag_machine_tool_stats():
    """
    统计RAG库中机器和刀具的使用次数
    
    Returns:
        dict: 每个工序最常用的机器和刀具
        {
            'milling': {'machine': 'm1m2', 'tool': 't1', 'machine_counts': {'m1m2': 10, 'm3m4': 8}, 'tool_counts': {'t1': 12, 't2': 8}},
            'drilling': {'machine': 'm1', 'tool': 't7', 'machine_counts': {'m1': 5, 'm2': 3}, 'tool_counts': {'t7': 6, 't8': 4}},
            'centre drilling': {'machine': 'm3', 'tool': 't10', 'machine_counts': {'m3': 15, 'm1': 10}, 'tool_counts': {'t10': 20}}
        }
    """
    from collections import defaultdict
    
    # 获取所有已审核且有表格数据的RAG特征
    approved_rags = RAGImageFeature.objects.filter(
        approval_status='approved',
        feature_table__isnull=False
    )
    
    # 统计每个工序的机器和刀具使用次数
    stats = {
        'milling': {'machine_counts': defaultdict(int), 'tool_counts': defaultdict(int)},
        'drilling': {'machine_counts': defaultdict(int), 'tool_counts': defaultdict(int)},
        'centre drilling': {'machine_counts': defaultdict(int), 'tool_counts': defaultdict(int)}
    }
    
    for rag in approved_rags:
        if not rag.feature_table:
            continue
            
        for row in rag.feature_table:
            operation = row.get('operation')
            if operation in stats:
                machine = row.get('machine', '')
                tool = row.get('tool', '')
                
                if machine:
                    machines = [m.strip() for m in machine.split(',')]
                    for m in machines:
                        stats[operation]['machine_counts'][m] += 1
                if tool:
                    # 处理多个工具的情况（如 "t1,t2"）
                    tools = [t.strip() for t in tool.split(',')]
                    for t in tools:
                        stats[operation]['tool_counts'][t] += 1
    
    # 找出每个工序最常用的机器和刀具
    result = {}
    for operation, data in stats.items():
        machine_counts = data['machine_counts']
        tool_counts = data['tool_counts']
        
        # 找出使用次数最多的机器
        most_used_machine = max(machine_counts.items(), key=lambda x: x[1])[0] if machine_counts else ''
        # 找出使用次数最多的刀具
        most_used_tool = max(tool_counts.items(), key=lambda x: x[1])[0] if tool_counts else ''
        
        result[operation] = {
            'machine': most_used_machine,
            'tool': most_used_tool,
            'machine_counts': dict(machine_counts),
            'tool_counts': dict(tool_counts)
        }
    
    return result