from users.models import CustomUser, StudentProfile, TeacherProfile
from academics.models import Course

def admin_dashboard_stats(request):
    """Add statistics to admin dashboard"""
    if request.user.is_authenticated and request.user.is_staff:
        return {
            'total_users': CustomUser.objects.count(),
            'total_students': StudentProfile.objects.count(),
            'total_teachers': TeacherProfile.objects.count(),
            'total_courses': Course.objects.count(),
        }
    return {}
