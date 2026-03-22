from django import forms
from .models import ProcessedImage, RAGImageFeature


class AdminRAGUploadForm(forms.Form):
    """管理员RAG上传表单 - 直接输入特征数据"""
    
    image = forms.ImageField(
        label='图片文件',
        help_text='上传机械零件图片，建议包含清晰的特征细节',
        widget=forms.FileInput(attrs={'class': 'form-control', 'accept': 'image/*'})
    )
    
    # 特征数量输入
    slot_count = forms.IntegerField(
        label='槽特征数量',
        min_value=0,
        initial=0,
        help_text='图片中槽特征的数量',
        widget=forms.NumberInput(attrs={'class': 'form-control', 'min': '0'})
    )
    
    hole_count = forms.IntegerField(
        label='孔特征数量',
        min_value=0,
        initial=0,
        help_text='图片中孔特征的数量',
        widget=forms.NumberInput(attrs={'class': 'form-control', 'min': '0'})
    )
    
    chamfer_count = forms.IntegerField(
        label='倒角特征数量',
        min_value=0,
        initial=0,
        help_text='图片中倒角特征的数量',
        widget=forms.NumberInput(attrs={'class': 'form-control', 'min': '0'})
    )
    
    shoulder_count = forms.IntegerField(
        label='肩特征数量',
        min_value=0,
        initial=0,
        help_text='图片中肩特征的数量',
        widget=forms.NumberInput(attrs={'class': 'form-control', 'min': '0'})
    )
    
    step_count = forms.IntegerField(
        label='阶特征数量',
        min_value=0,
        initial=0,
        help_text='图片中阶特征的数量',
        widget=forms.NumberInput(attrs={'class': 'form-control', 'min': '0'})
    )
    
    # 特征位置描述（可选）
    slot_positions = forms.CharField(
        label='槽特征位置描述',
        required=False,
        help_text='描述槽特征在图片中的位置，如：左侧边缘有2个矩形槽，中间有1个T型槽',
        widget=forms.Textarea(attrs={
            'class': 'form-control', 
            'rows': 2,
            'placeholder': '例如：左侧边缘有2个矩形槽，中间有1个T型槽'
        })
    )
    
    hole_positions = forms.CharField(
        label='孔特征位置描述',
        required=False,
        help_text='描述孔特征在图片中的位置，如：中心区域有3个圆孔，右下角有1个方孔',
        widget=forms.Textarea(attrs={
            'class': 'form-control', 
            'rows': 2,
            'placeholder': '例如：中心区域有3个圆孔，右下角有1个方孔'
        })
    )
    
    chamfer_positions = forms.CharField(
        label='倒角特征位置描述',
        required=False,
        help_text='描述倒角特征在图片中的位置，如：所有外边缘都有倒角，内孔边缘也有倒角',
        widget=forms.Textarea(attrs={
            'class': 'form-control', 
            'rows': 2,
            'placeholder': '例如：所有外边缘都有倒角，内孔边缘也有倒角'
        })
    )
    
    shoulder_positions = forms.CharField(
        label='肩特征位置描述',
        required=False,
        help_text='描述肩特征在图片中的位置，如：轴左侧有1个轴肩，右侧有2个台阶肩',
        widget=forms.Textarea(attrs={
            'class': 'form-control', 
            'rows': 2,
            'placeholder': '例如：轴左侧有1个轴肩，右侧有2个台阶肩'
        })
    )
    
    step_positions = forms.CharField(
        label='阶特征位置描述',
        required=False,
        help_text='描述阶特征在图片中的位置，如：左侧有2个高度台阶，右侧有1个平台台阶',
        widget=forms.Textarea(attrs={
            'class': 'form-control', 
            'rows': 2,
            'placeholder': '例如：左侧有2个高度台阶，右侧有1个平台台阶'
        })
    )
    
    # 其他信息
    description = forms.CharField(
        label='图片描述',
        required=False,
        help_text='对图片内容的简要描述',
        widget=forms.Textarea(attrs={
            'class': 'form-control', 
            'rows': 2,
            'placeholder': '例如：这是一个包含多个槽和孔的机械零件'
        })
    )