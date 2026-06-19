from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Course, Enrollment, Module, Lesson

@login_required
def academics_dashboard(request):
    user = request.user
    context = {'user': user, 'role': user.role}
    
    if user.role == 'student' and hasattr(user, 'student_profile'):
        enrollments = Enrollment.objects.filter(student=user.student_profile, is_active=True)
        context['enrollments'] = enrollments
        context['courses'] = [e.course for e in enrollments]
    elif user.role == 'teacher' and hasattr(user, 'teacher_profile'):
        context['courses'] = Course.objects.filter(teacher=user.teacher_profile)
    else:
        context['courses'] = Course.objects.filter(is_published=True)
    
    return render(request, 'academics/dashboard.html', context)

@login_required
def course_detail(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    modules = Module.objects.filter(course=course, is_published=True)
    return render(request, 'academics/course_detail.html', {'course': course, 'modules': modules})

@login_required
def lesson_detail(request, lesson_id):
    lesson = get_object_or_404(Lesson, id=lesson_id)
    return render(request, 'academics/lesson_detail.html', {'lesson': lesson})
