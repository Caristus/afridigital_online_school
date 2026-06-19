from django.urls import path
from . import views

urlpatterns = [
    path('', views.communication_dashboard, name='communication_dashboard'),
]
