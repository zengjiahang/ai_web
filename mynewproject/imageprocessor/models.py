from django.db import models
import json


class ProcessedImage(models.Model):
    """Processed image record"""
    image = models.ImageField('Uploaded Image', upload_to='uploads/%Y/%m/%d/')
    result = models.TextField('Kimi Analysis Result', blank=True)
    uploaded_at = models.DateTimeField('Upload Time', auto_now_add=True)
    processed_at = models.DateTimeField('Processing Time', null=True, blank=True)
    status = models.CharField('Status', max_length=20, choices=[
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ], default='pending')
    
    # 上传类型
    UPLOAD_TYPE_CHOICES = [
        ('user', '用户上传'),
        ('admin_rag', '管理员RAG上传'),
    ]
    upload_type = models.CharField(
        '上传类型', 
        max_length=20, 
        choices=UPLOAD_TYPE_CHOICES, 
        default='user'
    )
    
    class Meta:
        verbose_name = 'Processed Image'
        verbose_name_plural = 'Processed Images'
        ordering = ['-uploaded_at']
    
    def __str__(self):
        return f"Image {self.id} - {self.status}"


class RAGImageFeature(models.Model):
    """RAG系统图片特征标注"""
    processed_image = models.OneToOneField(ProcessedImage, on_delete=models.CASCADE, related_name='rag_features')
    
    # 特征数量（人工标注）
    slot_count = models.IntegerField('槽特征数量', default=0)
    hole_count = models.IntegerField('孔特征数量', default=0)
    chamfer_count = models.IntegerField('倒角特征数量', default=0)
    shoulder_count = models.IntegerField('肩特征数量', default=0)
    step_count = models.IntegerField('阶特征数量', default=0)
    
    # 特征位置描述（人工标注）
    slot_positions = models.TextField('槽特征位置描述', blank=True)
    hole_positions = models.TextField('孔特征位置描述', blank=True)
    chamfer_positions = models.TextField('倒角特征位置描述', blank=True)
    shoulder_positions = models.TextField('肩特征位置描述', blank=True)
    step_positions = models.TextField('阶特征位置描述', blank=True)
    
    # 特征向量（用于相似度计算）
    feature_vector = models.JSONField('特征向量', default=dict, blank=True)
    
    # 图片特征向量（用于图像相似度）- 预留字段，暂时不使用
    # image_embedding = models.JSONField('图片嵌入向量', default=list, blank=True)
    
    # 审核状态
    APPROVAL_STATUS_CHOICES = [
        ('pending_review', '待审核'),
        ('approved', '已审核'),
        ('rejected', '已拒绝'),
    ]
    approval_status = models.CharField(
        '审核状态', 
        max_length=20, 
        choices=APPROVAL_STATUS_CHOICES, 
        default='pending_review'
    )
    
    # 审核备注
    review_notes = models.TextField('审核备注', blank=True)
    
    # 审核者（预留）
    reviewed_by = models.CharField('审核者', max_length=100, blank=True)
    
    # 审核时间
    reviewed_at = models.DateTimeField('审核时间', null=True, blank=True)
    
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)
    
    class Meta:
        verbose_name = 'RAG图片特征'
        verbose_name_plural = 'RAG图片特征'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"RAG特征 - 图片{self.processed_image.id}"
    
    def get_total_features(self):
        """获取总特征数量"""
        return self.slot_count + self.hole_count + self.chamfer_count + self.shoulder_count + self.step_count
    
    def get_feature_vector_list(self):
        """获取特征向量列表"""
        return [
            self.slot_count,
            self.hole_count,
            self.chamfer_count,
            self.shoulder_count,
            self.step_count
        ]
    
    def update_feature_vector(self):
        """更新特征向量"""
        self.feature_vector = {
            'slot': self.slot_count,
            'hole': self.hole_count,
            'chamfer': self.chamfer_count,
            'shoulder': self.shoulder_count,
            'step': self.step_count,
            'total': self.get_total_features(),
            'approval_status': self.approval_status,
            'reviewed_at': str(self.reviewed_at) if self.reviewed_at else None
        }
        self.save(update_fields=['feature_vector'])
    
    def approve_feature(self, reviewed_by='', review_notes=''):
        """审核通过特征"""
        from django.utils import timezone
        self.approval_status = 'approved'
        self.reviewed_by = reviewed_by
        self.review_notes = review_notes
        self.reviewed_at = timezone.now()
        self.save()
        self.update_feature_vector()
    
    def reject_feature(self, reviewed_by='', review_notes=''):
        """拒绝特征"""
        from django.utils import timezone
        self.approval_status = 'rejected'
        self.reviewed_by = reviewed_by
        self.review_notes = review_notes
        self.reviewed_at = timezone.now()
        self.save()
        self.update_feature_vector()
    
    def has_positions(self):
        """检查是否有位置标注"""
        return bool(
            self.slot_positions or 
            self.hole_positions or 
            self.chamfer_positions or 
            self.shoulder_positions or 
            self.step_positions
        )