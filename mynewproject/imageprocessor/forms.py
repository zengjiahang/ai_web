from django import forms
from .models import ProcessedImage, RAGImageFeature


class ImageUploadForm(forms.ModelForm):
    """Image upload form"""
    class Meta:
        model = ProcessedImage
        fields = ['image']
        widgets = {
            'image': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/jpeg,image/jpg,image/png,image/gif,image/bmp,image/webp',
                'id': 'imageInput',
                'style': 'display: none;'  # 隐藏原生文件输入，使用自定义按钮
            })
        }
    
    def clean_image(self):
        """Validate image file"""
        image = self.cleaned_data.get('image')
        if image:
            # Check file size (limit to 10MB)
            if image.size > 10 * 1024 * 1024:
                raise forms.ValidationError('Image file size cannot exceed 10MB')
            
            # Check file type
            valid_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp']
            ext = image.name.lower().split('.')[-1]
            if f'.{ext}' not in valid_extensions:
                raise forms.ValidationError('Unsupported image format. Please upload JPG, PNG, GIF, BMP, or WebP format images')
        
        return image


class RAGFeatureAnnotationForm(forms.ModelForm):
    """RAG特征标注表单"""
    
    class Meta:
        model = RAGImageFeature
        fields = [
            'slot_count', 'hole_count', 'chamfer_count', 'shoulder_count', 'step_count',
            'slot_positions', 'hole_positions', 'chamfer_positions', 
            'shoulder_positions', 'step_positions'
        ]
        widgets = {
            'slot_count': forms.NumberInput(attrs={
                'class': 'form-control', 'min': '0', 'placeholder': '槽特征数量'
            }),
            'hole_count': forms.NumberInput(attrs={
                'class': 'form-control', 'min': '0', 'placeholder': '孔特征数量'
            }),
            'chamfer_count': forms.NumberInput(attrs={
                'class': 'form-control', 'min': '0', 'placeholder': '倒角特征数量'
            }),
            'shoulder_count': forms.NumberInput(attrs={
                'class': 'form-control', 'min': '0', 'placeholder': '肩特征数量'
            }),
            'step_count': forms.NumberInput(attrs={
                'class': 'form-control', 'min': '0', 'placeholder': '阶特征数量'
            }),
            'slot_positions': forms.Textarea(attrs={
                'class': 'form-control', 'rows': 2, 'placeholder': '描述槽特征的位置，例如：顶部半圆槽、底部矩形槽等'
            }),
            'hole_positions': forms.Textarea(attrs={
                'class': 'form-control', 'rows': 2, 'placeholder': '描述孔特征的位置，例如：顶部通孔、侧面螺纹孔等'
            }),
            'chamfer_positions': forms.Textarea(attrs={
                'class': 'form-control', 'rows': 2, 'placeholder': '描述倒角特征的位置，例如：边缘倒角、棱角倒角等'
            }),
            'shoulder_positions': forms.Textarea(attrs={
                'class': 'form-control', 'rows': 2, 'placeholder': '描述肩特征的位置，例如：轴肩、台阶肩等'
            }),
            'step_positions': forms.Textarea(attrs={
                'class': 'form-control', 'rows': 2, 'placeholder': '描述阶特征的位置，例如：高度台阶、平台台阶等'
            }),
        }
        labels = {
            'slot_count': '槽特征数量',
            'hole_count': '孔特征数量',
            'chamfer_count': '倒角特征数量',
            'shoulder_count': '肩特征数量',
            'step_count': '阶特征数量',
            'slot_positions': '槽特征位置描述',
            'hole_positions': '孔特征位置描述',
            'chamfer_positions': '倒角特征位置描述',
            'shoulder_positions': '肩特征位置描述',
            'step_positions': '阶特征位置描述',
        }
        help_texts = {
            'slot_count': '请输入槽特征的总数量',
            'hole_count': '请输入孔特征的总数量',
            'chamfer_count': '请输入倒角特征的总数量',
            'shoulder_count': '请输入肩特征的总数量',
            'step_count': '请输入阶特征的总数量',
            'slot_positions': '请详细描述各个槽特征的具体位置',
            'hole_positions': '请详细描述各个孔特征的具体位置',
            'chamfer_positions': '请详细描述各个倒角特征的具体位置',
            'shoulder_positions': '请详细描述各个肩特征的具体位置',
            'step_positions': '请详细描述各个阶特征的具体位置',
        }