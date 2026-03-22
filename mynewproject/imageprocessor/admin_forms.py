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
    
    # 特征位置标注（可选）
    slot_positions = forms.CharField(
        label='槽特征位置',
        required=False,
        help_text='槽特征在图片中的位置坐标，格式如: [[x1,y1],[x2,y2]]',
        widget=forms.Textarea(attrs={
            'class': 'form-control', 
            'rows': 2,
            'placeholder': '[[100, 150], [200, 250]]'
        })
    )
    
    hole_positions = forms.CharField(
        label='孔特征位置',
        required=False,
        help_text='孔特征在图片中的位置坐标，格式如: [[x1,y1],[x2,y2]]',
        widget=forms.Textarea(attrs={
            'class': 'form-control', 
            'rows': 2,
            'placeholder': '[[150, 200], [300, 400]]'
        })
    )
    
    chamfer_positions = forms.CharField(
        label='倒角特征位置',
        required=False,
        help_text='倒角特征在图片中的位置坐标，格式如: [[x1,y1],[x2,y2]]',
        widget=forms.Textarea(attrs={
            'class': 'form-control', 
            'rows': 2,
            'placeholder': '[[50, 100], [400, 450]]'
        })
    )
    
    shoulder_positions = forms.CharField(
        label='肩特征位置',
        required=False,
        help_text='肩特征在图片中的位置坐标，格式如: [[x1,y1],[x2,y2]]',
        widget=forms.Textarea(attrs={
            'class': 'form-control', 
            'rows': 2,
            'placeholder': '[[200, 300], [500, 600]]'
        })
    )
    
    step_positions = forms.CharField(
        label='阶特征位置',
        required=False,
        help_text='阶特征在图片中的位置坐标，格式如: [[x1,y1],[x2,y2]]',
        widget=forms.Textarea(attrs={
            'class': 'form-control', 
            'rows': 2,
            'placeholder': '[[250, 350], [600, 700]]'
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
    
    def clean_slot_positions(self):
        """验证槽特征位置格式"""
        data = self.cleaned_data.get('slot_positions', '')
        if data:
            try:
                import json
                positions = json.loads(data)
                if not isinstance(positions, list):
                    raise forms.ValidationError('位置数据必须是列表格式')
                for pos in positions:
                    if not isinstance(pos, list) or len(pos) != 2:
                        raise forms.ValidationError('每个位置必须是包含2个数字的列表')
                    if not all(isinstance(x, (int, float)) for x in pos):
                        raise forms.ValidationError('位置坐标必须是数字')
                return positions
            except json.JSONDecodeError:
                raise forms.ValidationError('位置数据必须是有效的JSON格式')
        return []
    
    def clean_hole_positions(self):
        """验证孔特征位置格式"""
        data = self.cleaned_data.get('hole_positions', '')
        if data:
            try:
                import json
                positions = json.loads(data)
                if not isinstance(positions, list):
                    raise forms.ValidationError('位置数据必须是列表格式')
                for pos in positions:
                    if not isinstance(pos, list) or len(pos) != 2:
                        raise forms.ValidationError('每个位置必须是包含2个数字的列表')
                    if not all(isinstance(x, (int, float)) for x in pos):
                        raise forms.ValidationError('位置坐标必须是数字')
                return positions
            except json.JSONDecodeError:
                raise forms.ValidationError('位置数据必须是有效的JSON格式')
        return []
    
    def clean_chamfer_positions(self):
        """验证倒角特征位置格式"""
        data = self.cleaned_data.get('chamfer_positions', '')
        if data:
            try:
                import json
                positions = json.loads(data)
                if not isinstance(positions, list):
                    raise forms.ValidationError('位置数据必须是列表格式')
                for pos in positions:
                    if not isinstance(pos, list) or len(pos) != 2:
                        raise forms.ValidationError('每个位置必须是包含2个数字的列表')
                    if not all(isinstance(x, (int, float)) for x in pos):
                        raise forms.ValidationError('位置坐标必须是数字')
                return positions
            except json.JSONDecodeError:
                raise forms.ValidationError('位置数据必须是有效的JSON格式')
        return []
    
    def clean_shoulder_positions(self):
        """验证肩特征位置格式"""
        data = self.cleaned_data.get('shoulder_positions', '')
        if data:
            try:
                import json
                positions = json.loads(data)
                if not isinstance(positions, list):
                    raise forms.ValidationError('位置数据必须是列表格式')
                for pos in positions:
                    if not isinstance(pos, list) or len(pos) != 2:
                        raise forms.ValidationError('每个位置必须是包含2个数字的列表')
                    if not all(isinstance(x, (int, float)) for x in pos):
                        raise forms.ValidationError('位置坐标必须是数字')
                return positions
            except json.JSONDecodeError:
                raise forms.ValidationError('位置数据必须是有效的JSON格式')
        return []
    
    def clean_step_positions(self):
        """验证阶特征位置格式"""
        data = self.cleaned_data.get('step_positions', '')
        if data:
            try:
                import json
                positions = json.loads(data)
                if not isinstance(positions, list):
                    raise forms.ValidationError('位置数据必须是列表格式')
                for pos in positions:
                    if not isinstance(pos, list) or len(pos) != 2:
                        raise forms.ValidationError('每个位置必须是包含2个数字的列表')
                    if not all(isinstance(x, (int, float)) for x in pos):
                        raise forms.ValidationError('位置坐标必须是数字')
                return positions
            except json.JSONDecodeError:
                raise forms.ValidationError('位置数据必须是有效的JSON格式')
        return []