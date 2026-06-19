from django.urls import path
from . import views

urlpatterns = [
    path('', views.transport_dashboard, name='transport_dashboard'),
]
