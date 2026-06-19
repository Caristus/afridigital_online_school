from django.urls import path
from . import views

urlpatterns = [
    path('', views.transcripts_dashboard, name='transcripts_dashboard'),
    path('report/<uuid:transcript_id>/', views.generate_report_card, name='generate_report_card'),
    path('analytics/', views.student_analytics, name='student_analytics'),
    path('analytics/student/<uuid:student_id>/', views.student_analytics, name='student_analytics_detail'),
    path('analytics/class/<uuid:class_id>/', views.class_analytics, name='class_analytics'),
    path('create/<uuid:student_id>/<uuid:term_id>/', views.create_transcript, name='create_transcript'),
    
    # New upload and management URLs
    path('upload-marks/', views.upload_marks, name='upload_marks'),
    path('class-list/', views.class_list, name='class_list'),
    path('class-list/<uuid:class_id>/', views.class_list, name='class_list_detail'),
    path('bulk-register/', views.bulk_register_students, name='bulk_register_students'),
    path('enter-marks/', views.enter_marks, name='enter_marks'),
]
