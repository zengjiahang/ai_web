from django.urls import path
from . import views
from . import rag_views
from . import dual_upload_views
from . import rag_admin_views

app_name = 'imageprocessor'

urlpatterns = [
    # 用户上传路径
    path('', dual_upload_views.UserImageUploadView.as_view(), name='user_upload'),
    path('api/upload/', views.ImageUploadAPIView.as_view(), name='api_upload'),
    path('result/<int:image_id>/', views.result_view, name='result'),
    path('history/', views.history_view, name='history'),
    
    # 工艺选择API
    path('api/save-process-selections/', views.SaveProcessSelectionsAPIView.as_view(), name='save_process_selections'),
    path('api/get-process-selections/', views.GetProcessSelectionsAPIView.as_view(), name='get_process_selections'),
    
    # 管理员RAG上传路径 - 避免与admin冲突
    path('rag-admin/upload/', dual_upload_views.AdminRAGUploadView.as_view(), name='admin_rag_upload'),
    
    # RAG相关URL
    path('rag/annotate/<int:image_id>/', rag_views.RAGAnnotationView.as_view(), name='rag_annotation'),
    path('rag/features/', rag_views.rag_feature_list, name='rag_feature_list'),
    path('rag/review/', rag_views.RAGReviewView.as_view(), name='rag_review'),
    path('rag/feature/<int:feature_id>/', rag_views.rag_feature_detail, name='rag_feature_detail'),
    
    # 管理员功能
    path('rag/delete/<int:feature_id>/', rag_admin_views.delete_rag_feature, name='delete_rag_feature'),
    path('rag/bulk-delete/', rag_admin_views.bulk_delete_rag_features, name='bulk_delete_rag_features'),
    path('rag/edit/<int:feature_id>/', rag_admin_views.edit_rag_feature, name='edit_rag_feature'),
]