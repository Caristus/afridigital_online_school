from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.http import HttpResponse
from django.db.models import Q
from django.template.loader import render_to_string
from xhtml2pdf import pisa
from io import BytesIO

from .models import Timetable, ClassSession, Room
from academics.models import Class, Subject
from users.models import TeacherProfile
from core.models import Term, AcademicYear

def is_admin_or_system(user):
    return user.is_authenticated and (user.role in ['admin', 'system_admin'] or user.is_superuser)

@login_required
def timetable_dashboard(request):
    timetables = Timetable.objects.filter(is_active=True).select_related('class_assigned', 'term')
    return render(request, 'timetable/dashboard.html', {'timetables': timetables})

@login_required
@user_passes_test(is_admin_or_system)
def allocate_session(request):
    """Smart allocation with conflict detection"""
    if request.method == 'POST':
        timetable_id = request.POST.get('timetable')
        subject_id = request.POST.get('subject')
        teacher_id = request.POST.get('teacher')
        room_id = request.POST.get('room')
        day = request.POST.get('day')
        start_time = request.POST.get('start_time')
        end_time = request.POST.get('end_time')
        period_name = request.POST.get('period_name', '')

        timetable = get_object_or_404(Timetable, id=timetable_id)
        subject = get_object_or_404(Subject, id=subject_id)
        teacher = get_object_or_404(TeacherProfile, id=teacher_id)
        room = get_object_or_404(Room, id=room_id) if room_id else None

        # --- CONFLICT DETECTION ---
        conflicts = []
        
        # 1. Check if Teacher is busy
        if ClassSession.objects.filter(
            teacher=teacher, day=day,
            start_time__lt=end_time, end_time__gt=start_time
        ).exclude(timetable=timetable).exists():
            conflicts.append(f"Teacher {teacher} is already booked at this time.")

        # 2. Check if Room is busy
        if room and ClassSession.objects.filter(
            room=room, day=day,
            start_time__lt=end_time, end_time__gt=start_time
        ).exclude(timetable=timetable).exists():
            conflicts.append(f"Room {room} is already booked at this time.")

        # 3. Check if Class is busy
        if ClassSession.objects.filter(
            timetable=timetable, day=day,
            start_time__lt=end_time, end_time__gt=start_time
        ).exists():
            conflicts.append(f"Class {timetable.class_assigned} already has a lesson at this time.")

        if conflicts:
            for c in conflicts:
                messages.error(request, c)
            return redirect('allocate_session')

        # Save Session
        ClassSession.objects.create(
            timetable=timetable, subject=subject, teacher=teacher,
            room=room, day=day, start_time=start_time, end_time=end_time,
            period_name=period_name
        )
        messages.success(request, f'Successfully allocated {subject} to {teacher} on {day}!')
        return redirect('allocate_session')

    context = {
        'timetables': Timetable.objects.filter(is_active=True),
        'subjects': Subject.objects.all(),
        'teachers': TeacherProfile.objects.all(),
        'rooms': Room.objects.all(),
        'days': ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday']
    }
    return render(request, 'timetable/allocate.html', context)

def render_to_pdf(template_src, context_dict={}):
    template = render_to_string(template_src, context_dict)
    html = template
    result = BytesIO()
    pdf = pisa.pisaDocument(BytesIO(html.encode("UTF-8")), result)
    if not pdf.err:
        return HttpResponse(result.getvalue(), content_type='application/pdf')
    return HttpResponse("Error generating PDF", status=400)

@login_required
def generate_class_timetable_pdf(request, timetable_id):
    timetable = get_object_or_404(Timetable, id=timetable_id)
    sessions = ClassSession.objects.filter(timetable=timetable).select_related('subject', 'teacher', 'room')
    
    # Organize sessions into a grid: Days x Periods
    days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']
    # Get unique time slots
    time_slots = sessions.values_list('start_time', 'end_time', 'period_name').distinct().order_by('start_time')
    
    grid = {}
    for day in days:
        grid[day] = {}
        for start, end, pname in time_slots:
            session = sessions.filter(day=day, start_time=start, end_time=end).first()
            grid[day][(start, end)] = session

    context = {
        'timetable': timetable,
        'grid': grid,
        'time_slots': time_slots,
        'days': days
    }
    return render_to_pdf('timetable/class_pdf.html', context)

@login_required
def generate_teacher_timetable_pdf(request, teacher_id):
    teacher = get_object_or_404(TeacherProfile, id=teacher_id)
    sessions = ClassSession.objects.filter(teacher=teacher).select_related('subject', 'timetable__class_assigned', 'room')
    
    days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']
    time_slots = sessions.values_list('start_time', 'end_time').distinct().order_by('start_time')
    
    grid = {}
    for day in days:
        grid[day] = {}
        for start, end in time_slots:
            session = sessions.filter(day=day, start_time=start, end_time=end).first()
            grid[day][(start, end)] = session

    context = {
        'teacher': teacher,
        'grid': grid,
        'time_slots': time_slots,
        'days': days
    }
    return render_to_pdf('timetable/teacher_pdf.html', context)
