from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from . import views as config_views

urlpatterns = [
    # Custom Admin (replaces default Django admin)
    path('admin/login/', config_views.custom_login, name='custom_admin_login'),
    path('admin/logout/', config_views.custom_logout, name='custom_admin_logout'),
    path('admin/', config_views.custom_admin_dashboard, name='custom_admin_dashboard'),
    path('admin/users/', config_views.user_management, name='user_management'),
    path('admin/courses/', config_views.course_management, name='course_management'),
    path('admin/finance/', config_views.finance_management, name='finance_management'),
    
    # Keep default admin for superusers who need it (optional)
    path('django-admin/', admin.site.urls),
    
    # App URLs
    path('', include('users.urls')),
    path('academics/', include('academics.urls')),
    path('assessments/', include('assessments.urls')),
    path('finance/', include('finance.urls')),
    path('attendance/', include('attendance.urls')),
    path('transcripts/', include('transcripts.urls')),
    path('timetable/', include('timetable.urls')),
    path('communication/', include('communication.urls')),
    path('analytics/', include('analytics.urls')),
    path('library/', include('library.urls')),
    path('transport/', include('transport.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATICFILES_DIRS[0])
