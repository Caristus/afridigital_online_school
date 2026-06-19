from django.urls import path
from . import views

urlpatterns = [
    path('', views.library_dashboard, name='library_dashboard'),
]
