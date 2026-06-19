from django.urls import path
from . import views

urlpatterns = [
    path('', views.attendance_dashboard, name='attendance_dashboard'),
]
