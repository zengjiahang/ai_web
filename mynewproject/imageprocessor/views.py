from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.views import View
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

from .forms import ImageUploadForm
from .models import ProcessedImage, RAGImageFeature, ProcessSelection
from .kimi_service import KimiService

from .dual_upload_views import format_features_to_table
from .rag_views import get_rag_machine_tool_stats
import json
import os


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
            
            # 获取RAG库统计并格式化为完整5列表格（含Machine/Tool）
            rag_stats = get_rag_machine_tool_stats()
            table_data = format_features_to_table(features, rag_stats)
            print(f"Generated table data with {len(table_data)} rows")
            
        except Exception as e:
            print(f"Error extracting features for table: {e}")
            print(f"Result text: {processed_image.result[:200] if processed_image.result else 'None'}")
            table_data = []
    
    print(f"Final table_data: {table_data}")
    
    # 机器和刀具参考数据
    machine_refs = [
        ('m1', 'CNC vertical milling'),
        ('m2', 'three-axis vertical milling'),
        ('m3', 'drill press'),
        ('m4', 'horizontal milling'),
        ('m5', 'CNC horizontal milling'),
    ]
    tool_refs = [
        ('t1', 'End_mill(20,30)'), ('t2', 'End_mill(30,50)'), ('t3', 'End_mill(15,20)'),
        ('t4', 'End_mill(40,60)'), ('t5', 'Side_mill(50,10)'), ('t6', 'T_slot_cutter(30,15)'),
        ('t7', 'Drill(20,55)'), ('t8', 'Drill(30,50)'), ('t9', 'Drill(50,80)'),
        ('t10', 'Centre_drill(20,5)'), ('t11', 'Angle_cutter(40,45)'), ('t12', 'Drill(70,100)'),
        ('t13', 'Drill(8,30)'), ('t14', 'Drill(10,35)'), ('t15', 'T_slot_cutter(20,5)'),
        ('t16', 'Drill(5,30)'), ('t17', 'Drill(15,50)'),
    ]

    return render(request, 'imageprocessor/result.html', {
        'processed_image': processed_image,
        'table_data': table_data,
        'machine_refs': machine_refs,
        'tool_refs': tool_refs,
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
class SaveTableDataAPIView(View):
    """保存表格数据API"""
    
    def post(self, request):
        """保存表格数据"""
        try:
            image_id = request.GET.get('image_id')
            
            if not image_id:
                return JsonResponse({
                    'success': False,
                    'error': '缺少image_id参数'
                }, status=400)
            
            # 获取图片对象
            processed_image = get_object_or_404(ProcessedImage, id=image_id)
            
            # 解析表格数据
            request_data = json.loads(request.body)
            table_data = request_data.get('table_data', [])
            
            # 删除该图片的所有旧ProcessSelection记录
            ProcessSelection.objects.filter(processed_image=processed_image).delete()
            
            # 保存新的表格数据
            for index, row_data in enumerate(table_data):
                ProcessSelection.objects.create(
                    processed_image=processed_image,
                    feature_name=row_data.get('feature', ''),
                    operation=row_data.get('operation', ''),
                    prior_operations=row_data.get('prior_operations', ''),
                    sequence=index,  # 使用索引作为序号，确保唯一性
                    machine=row_data.get('machine', ''),
                    tool=row_data.get('tool', ''),
                    is_chamfer_second=False
                )
            
            return JsonResponse({
                'success': True,
                'message': '表格数据保存成功'
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