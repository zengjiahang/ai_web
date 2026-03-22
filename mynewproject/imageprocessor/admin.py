from django.contrib import admin
from .models import ProcessedImage, RAGImageFeature


@admin.register(ProcessedImage)
class ProcessedImageAdmin(admin.ModelAdmin):
    list_display = ['id', 'status', 'uploaded_at', 'processed_at']
    list_filter = ['status', 'uploaded_at']
    search_fields = ['id', 'result']
    readonly_fields = ['uploaded_at', 'processed_at']
    
    fieldsets = (
        ('基本信息', {
            'fields': ('image', 'status', 'uploaded_at', 'processed_at')
        }),
        ('分析结果', {
            'fields': ('result',)
        }),
    )


@admin.register(RAGImageFeature)
class RAGImageFeatureAdmin(admin.ModelAdmin):
    list_display = ['id', 'processed_image', 'get_total_features', 'created_at', 'updated_at']
    list_filter = ['created_at', 'updated_at']
    search_fields = ['id', 'processed_image__id']
    readonly_fields = ['created_at', 'updated_at', 'feature_vector']
    
    fieldsets = (
        ('关联图片', {
            'fields': ('processed_image',)
        }),
        ('特征数量', {
            'fields': (
                ('slot_count', 'hole_count'),
                ('chamfer_count', 'shoulder_count', 'step_count')
            )
        }),
        ('特征位置描述', {
            'fields': (
                'slot_positions',
                'hole_positions', 
                'chamfer_positions',
                'shoulder_positions',
                'step_positions'
            )
        }),
        ('系统信息', {
            'fields': ('feature_vector', 'created_at', 'updated_at')
        }),
    )
    
    def get_total_features(self, obj):
        return obj.get_total_features()
    get_total_features.short_description = '总特征数'