from django import forms
from .models import ProcessedImage


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