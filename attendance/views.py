from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import AttendanceRecord, AttendanceSession

@login_required
def attendance_dashboard(request):
    user = request.user
    context = {'user': user, 'role': user.role}
    
    if user.role == 'student' and hasattr(user, 'student_profile'):
        records = AttendanceRecord.objects.filter(student=user.student_profile)
        context['records'] = records
        total = records.count()
        present = records.filter(status='present').count()
        context['attendance_percentage'] = (present / total * 100) if total > 0 else 0
    else:
        context['sessions'] = AttendanceSession.objects.all()[:10]
    
    return render(request, 'attendance/dashboard.html', context)
