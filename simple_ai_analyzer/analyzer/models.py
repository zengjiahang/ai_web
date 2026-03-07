from django.db import models


class UploadedImage(models.Model):
    """上传的图片记录"""
    image = models.ImageField('上传的图片', upload_to='uploads/%Y/%m/%d/')
    result = models.TextField('分析结果', blank=True)
    uploaded_at = models.DateTimeField('上传时间', auto_now_add=True)
    
    class Meta:
        verbose_name = '上传图片'
        verbose_name_plural = '上传图片'
        ordering = ['-uploaded_at']
    
    def __str__(self):
        return f"图片 {self.id} - {self.image.name}"