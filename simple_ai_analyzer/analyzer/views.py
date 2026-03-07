from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.views import View
from .models import UploadedImage
import os
import base64
import re
from openai import OpenAI
from django.conf import settings


@method_decorator(csrf_exempt, name='dispatch')
class ImageAnalysisView(View):
    """图片分析视图"""
    
    def get(self, request):
        """显示上传页面"""
        return render(request, 'analyzer/upload.html')
    
    def post(self, request):
        """处理图片上传和分析"""
        try:
            # 获取上传的图片
            image_file = request.FILES.get('image')
            if not image_file:
                return JsonResponse({
                    'success': False,
                    'error': '请选择要上传的图片'
                })
            
            # 保存图片
            uploaded_image = UploadedImage.objects.create(image=image_file)
            
            # 分析图片
            result = analyze_image_features(uploaded_image.image.path)
            
            if result['success']:
                uploaded_image.result = result['result']
                uploaded_image.save()
                
                return JsonResponse({
                    'success': True,
                    'result': result['result'],
                    'features': result.get('features', {}),
                    'total': result.get('total', 0),
                    'image_url': uploaded_image.image.url
                })
            else:
                uploaded_image.delete()  # 删除失败的记录
                return JsonResponse({
                    'success': False,
                    'error': result['error']
                })
                
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': f'处理失败: {str(e)}'
            })


def analyze_image_features(image_path):
    """
    分析图片中的机械特征 - 使用test2.py的正确实现
    """
    try:
        # 初始化Kimi API客户端 - 使用test2.py的配置
        client = OpenAI(
            api_key=settings.KIMI_API_KEY,
            base_url=settings.KIMI_API_BASE_URL
        )
        
        # 读取图片文件 - 使用test2.py的方法
        with open(image_path, "rb") as f:
            image_data = f.read()
        
        # 使用test2.py的编码方式
        image_url = f"data:image/{os.path.splitext(image_path)[1]};base64,{base64.b64encode(image_data).decode('utf-8')}"
        
        # 调用Kimi Vision API - 完全按照test2.py的方式
        completion = client.chat.completions.create(
            model="kimi-k2.5",
            messages=[
                {"role": "system", "content": "你是 Kimi。"},
                {
                    "role": "user",
                    # 注意这里，content 由原来的 str 类型变更为一个 list，这个 list 中包含多个部分的内容，图片（image_url）是一个部分（part），
                    # 文字（text）是一个部分（part）
                    "content": [
                        {
                            "type": "image_url", # <-- 使用 image_url 类型来上传图片，内容为使用 base64 编码过的图片内容
                            "image_url": {
                                "url": image_url,
                            },
                        },
                        {
                            "type": "text",
                            "text": "请帮我分析图片里有几个槽特征，几个倒角特征，几个孔特征，几个阶特征，几个肩特征。", # <-- 使用 text 类型来提供文字指令，例如"描述图片内容"
                        },
                    ],
                },
            ],
        )
        
        # 获取原始响应内容
        result_content = completion.choices[0].message.content
        print(f"Kimi API原始响应: {repr(result_content)}")
        
        # 提取特征数量
        features = extract_features_from_text(result_content)
        total_features = sum(features.values())
        
        # 构建完整的结果
        full_result = f"{result_content}\n\n"
        full_result += "📊 特征数量统计:\n"
        full_result += "=" * 30 + "\n"
        for feature, count in features.items():
            full_result += f"{feature}: {count}个\n"
        full_result += f"\n🔢 总特征数量: {total_features}"
        
        return {
            'success': True,
            'result': full_result,
            'features': features,
            'total': total_features
        }
        
    except Exception as e:
        return {
            'success': False,
            'error': f'分析失败: {str(e)}'
        }


def extract_features_from_text(text):
    """
    从文本中提取特征数量 - 根据Kimi API的实际响应格式优化
    """
    features = {
        '槽特征': 0,
        '孔特征': 0,
        '倒角特征': 0,
        '肩特征': 0,
        '阶特征': 0
    }
    
    # 根据Kimi API的实际响应格式，使用更灵活的模式匹配
    import re
    
    # 槽特征 - 匹配"槽(特征)"后面跟的数字
    slot_match = re.search(r'槽(?:特征)?.*?\**(\d+)个\**', text, re.IGNORECASE)
    if slot_match:
        features['槽特征'] = int(slot_match.group(1))
    
    # 孔特征 - 匹配"孔(特征)"后面跟的数字  
    hole_match = re.search(r'孔(?:特征)?.*?\**(\d+)个\**', text, re.IGNORECASE)
    if hole_match:
        features['孔特征'] = int(hole_match.group(1))
    
    # 倒角特征 - 匹配"倒角(特征)"后面跟的数字
    chamfer_match = re.search(r'倒角(?:特征)?.*?\**(\d+)个\**', text, re.IGNORECASE)
    if chamfer_match:
        features['倒角特征'] = int(chamfer_match.group(1))
    
    # 肩特征 - 匹配"肩(特征)"后面跟的数字
    shoulder_match = re.search(r'肩(?:特征)?.*?\**(\d+)个\**', text, re.IGNORECASE)
    if shoulder_match:
        features['肩特征'] = int(shoulder_match.group(1))
    
    # 阶特征 - 匹配"阶(特征)"后面跟的数字
    step_match = re.search(r'阶(?:特征)?.*?\**(\d+)个\**', text, re.IGNORECASE)
    if step_match:
        features['阶特征'] = int(step_match.group(1))
    
    # 如果上述方法没有找到，尝试从表格格式中提取
    if all(count == 0 for count in features.values()):
        # 尝试从表格中提取
        table_matches = re.findall(r'\**(\d+)个\**', text)
        if len(table_matches) >= 5:
            # 假设顺序是：槽、孔、倒角、肩、阶
            features['槽特征'] = int(table_matches[0])
            features['孔特征'] = int(table_matches[1])
            features['倒角特征'] = int(table_matches[2])
            features['肩特征'] = int(table_matches[3])
            features['阶特征'] = int(table_matches[4])
    
    # 如果还是0，尝试从"最可能的标准答案"中提取
    if all(count == 0 for count in features.values()):
        final_answer_match = re.search(r'槽\((\d+)\).*?孔\((\d+)\).*?倒角\((\d+)\).*?阶\((\d+)\).*?肩\((\d+)\)', text, re.IGNORECASE)
        if final_answer_match:
            features['槽特征'] = int(final_answer_match.group(1))
            features['孔特征'] = int(final_answer_match.group(2))
            features['倒角特征'] = int(final_answer_match.group(3))
            features['阶特征'] = int(final_answer_match.group(4))
            features['肩特征'] = int(final_answer_match.group(5))
    
    return features