from django.db import models


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
    
    class Meta:
        verbose_name = 'Processed Image'
        verbose_name_plural = 'Processed Images'
        ordering = ['-uploaded_at']
    
    def __str__(self):
        return f"Image {self.id} - {self.status}"