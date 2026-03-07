from django.urls import path
from . import views

app_name = 'imageprocessor'

urlpatterns = [
    path('', views.ImageUploadView.as_view(), name='upload'),
    path('api/upload/', views.ImageUploadAPIView.as_view(), name='api_upload'),
    path('result/<int:image_id>/', views.result_view, name='result'),
    path('history/', views.history_view, name='history'),
]