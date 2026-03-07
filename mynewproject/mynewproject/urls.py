"""
URL configuration for mynewproject project.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

# Import error handlers
from imageprocessor import error_handlers

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('imageprocessor.urls')),
]

# Custom error handlers
handler404 = error_handlers.handler404
handler500 = error_handlers.handler500
handler403 = error_handlers.handler403
handler400 = error_handlers.handler400

# Serve media files in development mode
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)