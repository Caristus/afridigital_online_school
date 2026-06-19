from django.urls import path
from . import views

urlpatterns = [
    path('', views.assessments_dashboard, name='assessments_dashboard'),
    path('submit/<uuid:assessment_id>/', views.submit_assessment, name='submit_assessment'),
    path('grade/<uuid:submission_id>/', views.view_grade, name='view_grade'),
]
