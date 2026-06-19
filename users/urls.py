from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('', views.user_login, name='login'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('logout/', auth_views.LogoutView.as_view(next_page='login'), name='logout'),
    
    # Bulk Upload URLs (System Admin only)
    path('bulk-upload/subjects/', views.bulk_upload_subjects, name='bulk_upload_subjects'),
    path('bulk-upload/teachers/', views.bulk_upload_teachers, name='bulk_upload_teachers'),
    path('bulk-upload/classes/', views.bulk_upload_classes, name='bulk_upload_classes'),
    path('bulk-upload/classlist/', views.bulk_upload_classlist, name='bulk_upload_classlist'),
    path('bulk-upload/marks/', views.bulk_upload_marks, name='bulk_upload_marks'),
    path('download-template/<str:template_type>/', views.download_template, name='download_template'),
]
