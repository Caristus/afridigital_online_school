from django.urls import path
from . import views

urlpatterns = [
    path('', views.timetable_dashboard, name='timetable_dashboard'),
    path('allocate/', views.allocate_session, name='allocate_session'),
    path('pdf/class/<uuid:timetable_id>/', views.generate_class_timetable_pdf, name='generate_class_timetable_pdf'),
    path('pdf/teacher/<uuid:teacher_id>/', views.generate_teacher_timetable_pdf, name='generate_teacher_timetable_pdf'),
]
