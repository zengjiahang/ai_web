from django.contrib import admin
from .models import ProcessedImage


@admin.register(ProcessedImage)
class ProcessedImageAdmin(admin.ModelAdmin):
    list_display = ['id', 'image_preview', 'status', 'uploaded_at', 'processed_at']
    list_filter = ['status', 'uploaded_at', 'processed_at']
    search_fields = ['result']
    readonly_fields = ['image_preview', 'uploaded_at', 'processed_at']
    
    def image_preview(self, obj):
        """Display image preview"""
        if obj.image:
            return f'<img src="{obj.image.url}" width="100" height="100" style="object-fit: cover;" />'
        return "No Image"
    
    image_preview.short_description = 'Image Preview'