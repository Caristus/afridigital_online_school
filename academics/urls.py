from django.urls import path
from . import views

urlpatterns = [
    path('', views.academics_dashboard, name='academics_dashboard'),
    path('course/<uuid:course_id>/', views.course_detail, name='course_detail'),
    path('lesson/<uuid:lesson_id>/', views.lesson_detail, name='lesson_detail'),
]
