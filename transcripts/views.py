from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import HttpResponse, JsonResponse
from django.contrib import messages
from django.template.loader import render_to_string
from django.db.models import Avg, Max, Min, Count, Q
from django.utils import timezone
from .models import (
    Transcript, AcademicRecord, GPAConfig, GradePoint,
    SubjectPerformance, BehavioralReport, ReportCardTemplate
)
from users.models import StudentProfile, TeacherProfile, User
from academics.models import Course, Subject, Class
from core.models import Term, AcademicYear
from attendance.models import AttendanceRecord
import json
import csv
from io import TextIOWrapper
from datetime import datetime


@login_required
def transcripts_dashboard(request):
    """Main transcripts dashboard"""
    user = request.user
    context = {'user': user, 'role': user.role}
    
    if user.role == 'student' and hasattr(user, 'student_profile'):
        context['transcripts'] = Transcript.objects.filter(
            student=user.student_profile,
            status='published'
        ).order_by('-academic_year__name', '-term__name')
        context['latest_transcript'] = context['transcripts'].first()
        
        if context['latest_transcript']:
            context['gpa'] = context['latest_transcript'].gpa
            context['average'] = context['latest_transcript'].average_marks
            context['position'] = context['latest_transcript'].class_position
    else:
        context['transcripts'] = Transcript.objects.filter(
            status='published'
        ).select_related('student', 'term', 'academic_year').order_by('-created_at')[:50]
        context['pending_transcripts'] = Transcript.objects.filter(
            status='pending_approval'
        ).count()
    
    return render(request, 'transcripts/dashboard.html', context)


@login_required
def generate_report_card(request, transcript_id):
    """Generate PDF report card"""
    transcript = get_object_or_404(Transcript, id=transcript_id)
    
    if request.user.role == 'student':
        if transcript.student.student != request.user:
            return redirect('transcripts_dashboard')
    
    records = AcademicRecord.objects.filter(
        student=transcript.student,
        term=transcript.term,
        academic_year=transcript.academic_year
    ).select_related('course__subject')
    
    try:
        behavioral = BehavioralReport.objects.get(
            student=transcript.student,
            term=transcript.term,
            academic_year=transcript.academic_year
        )
    except BehavioralReport.DoesNotExist:
        behavioral = None
    
    attendance_records = AttendanceRecord.objects.filter(
        student=transcript.student,
        session__term=transcript.term
    )
    total_days = attendance_records.count()
    present_days = attendance_records.filter(status='present').count()
    
    template = ReportCardTemplate.objects.filter(is_default=True).first()
    if not template:
        template = ReportCardTemplate.objects.first()
    
    context = {
        'transcript': transcript,
        'records': records,
        'behavioral': behavioral,
        'attendance': {
            'total': total_days,
            'present': present_days,
            'percentage': (present_days/total_days*100) if total_days > 0 else 0
        },
        'template': template,
        'generated_date': timezone.now().strftime('%d %B %Y'),
    }
    
    html_string = render_to_string('transcripts/report_card.html', context)
    return HttpResponse(html_string)


@login_required
def student_analytics(request, student_id=None):
    """Analytics dashboard for student performance"""
    user = request.user
    
    if student_id:
        student = get_object_or_404(StudentProfile, id=student_id)
    elif user.role == 'student' and hasattr(user, 'student_profile'):
        student = user.student_profile
    else:
        return redirect('transcripts_dashboard')
    
    if user.role == 'student' and student.student != user:
        return redirect('transcripts_dashboard')
    
    context = {'student': student, 'user': user}
    
    transcripts = Transcript.objects.filter(
        student=student,
        status='published'
    ).order_by('academic_year__name', 'term__name')
    
    context['transcripts'] = transcripts
    
    if transcripts.exists():
        performance_data = []
        for t in transcripts:
            performance_data.append({
                'term': f"{t.term.name} {t.academic_year.name}",
                'average': float(t.average_marks),
                'gpa': float(t.gpa),
                'position': t.class_position
            })
        context['performance_data'] = json.dumps(performance_data)
        
        subject_performances = SubjectPerformance.objects.filter(
            student=student
        ).select_related('subject')
        
        subject_data = []
        for sp in subject_performances:
            subject_data.append({
                'subject': sp.subject.name,
                'term1': float(sp.term1_score) if sp.term1_score else 0,
                'term2': float(sp.term2_score) if sp.term2_score else 0,
                'term3': float(sp.term3_score) if sp.term3_score else 0,
                'average': float(sp.average_score)
            })
        context['subject_data'] = json.dumps(subject_data)
        
        latest = transcripts.last()
        context['latest_transcript'] = latest
        
        context['records'] = AcademicRecord.objects.filter(
            student=student,
            term=latest.term,
            academic_year=latest.academic_year
        ).select_related('course__subject')
        
        if student.current_class:
            class_students = StudentProfile.objects.filter(current_class=student.current_class)
            class_transcripts = Transcript.objects.filter(
                student__in=class_students,
                term=latest.term,
                academic_year=latest.academic_year,
                status='published'
            )
            
            if class_transcripts.exists():
                context['class_average'] = class_transcripts.aggregate(Avg('average_marks'))['average_marks__avg']
                context['class_best'] = class_transcripts.aggregate(Max('average_marks'))['average_marks__max']
                context['class_worst'] = class_transcripts.aggregate(Min('average_marks'))['average_marks__min']
    
    return render(request, 'transcripts/analytics.html', context)


@login_required
def class_analytics(request, class_id=None):
    """Analytics for entire class"""
    user = request.user
    
    if not (user.role in ['teacher', 'admin'] or user.is_superuser):
        return redirect('transcripts_dashboard')
    
    if class_id:
        class_obj = get_object_or_404(Class, id=class_id)
    else:
        class_obj = Class.objects.first()
        if not class_obj:
            return redirect('transcripts_dashboard')
    
    context = {'class_obj': class_obj, 'user': user}
    
    current_term = Term.objects.filter(is_current=True).first()
    current_year = AcademicYear.objects.filter(is_current=True).first()
    
    if current_term and current_year:
        students = StudentProfile.objects.filter(current_class=class_obj)
        
        transcripts = Transcript.objects.filter(
            student__in=students,
            term=current_term,
            academic_year=current_year,
            status='published'
        )
        
        context['transcripts'] = transcripts
        context['total_students'] = students.count()
        context['with_transcripts'] = transcripts.count()
        
        if transcripts.exists():
            context['average'] = transcripts.aggregate(Avg('average_marks'))['average_marks__avg']
            context['highest'] = transcripts.aggregate(Max('average_marks'))['average_marks__max']
            context['lowest'] = transcripts.aggregate(Min('average_marks'))['average_marks__min']
            
            grade_dist = transcripts.values('gpa').annotate(count=Count('id'))
            context['grade_distribution'] = list(grade_dist)
            
            context['top_performers'] = transcripts.order_by('-average_marks')[:10]
            
            records = AcademicRecord.objects.filter(
                student__in=students,
                term=current_term,
                academic_year=current_year
            ).values('course__subject__name').annotate(
                avg_score=Avg('total_score'),
                highest=Max('total_score'),
                lowest=Min('total_score')
            )
            context['subject_performance'] = list(records)
    
    return render(request, 'transcripts/class_analytics.html', context)


@login_required
def create_transcript(request, student_id, term_id):
    """Create or update transcript for a student"""
    student = get_object_or_404(StudentProfile, id=student_id)
    term = get_object_or_404(Term, id=term_id)
    academic_year = term.academic_year
    
    transcript, created = Transcript.objects.get_or_create(
        student=student,
        term=term,
        academic_year=academic_year,
        defaults={'status': 'draft'}
    )
    
    if request.method == 'POST':
        transcript.general_remarks = request.POST.get('general_remarks', '')
        transcript.class_teacher_remarks = request.POST.get('class_teacher_remarks', '')
        transcript.principal_remarks = request.POST.get('principal_remarks', '')
        transcript.conduct_grade = request.POST.get('conduct_grade', 'A')
        
        transcript.calculate_results()
        
        if 'approve' in request.POST:
            transcript.status = 'approved'
            transcript.approved_by = request.user.teacher_profile if hasattr(request.user, 'teacher_profile') else None
            transcript.approved_date = timezone.now()
        elif 'publish' in request.POST:
            transcript.status = 'published'
        
        transcript.save()
        
        return redirect('transcripts_dashboard')
    
    records = AcademicRecord.objects.filter(
        student=student,
        term=term,
        academic_year=academic_year
    ).select_related('course__subject')
    
    attendance_records = AttendanceRecord.objects.filter(
        student=student,
        session__term=term
    )
    transcript.days_present = attendance_records.filter(status='present').count()
    transcript.days_absent = attendance_records.filter(status='absent').count()
    total = transcript.days_present + transcript.days_absent
    transcript.attendance_percentage = (transcript.days_present/total*100) if total > 0 else 0
    
    context = {
        'student': student,
        'term': term,
        'academic_year': academic_year,
        'transcript': transcript,
        'records': records,
        'created': created,
    }
    
    return render(request, 'transcripts/create_transcript.html', context)


@login_required
def upload_marks(request):
    """Bulk upload marks via CSV/Excel"""
    if not (request.user.role in ['teacher', 'admin'] or request.user.is_superuser):
        messages.error(request, 'Permission denied.')
        return redirect('dashboard')
    
    context = {'user': request.user}
    
    if request.method == 'POST' and request.FILES.get('marks_file'):
        uploaded_file = request.FILES['marks_file']
        course_id = request.POST.get('course')
        term_id = request.POST.get('term')
        
        try:
            course = Course.objects.get(id=course_id)
            term = Term.objects.get(id=term_id)
            
            if uploaded_file.name.endswith('.csv'):
                text_file = TextIOWrapper(uploaded_file.file, encoding='utf-8')
                reader = csv.reader(text_file)
                next(reader)  # Skip header
                
                success_count = 0
                error_count = 0
                
                for row in reader:
                    try:
                        admission_no = row[0].strip()
                        ca1 = float(row[1]) if row[1] else 0
                        ca2 = float(row[2]) if row[2] else 0
                        ca3 = float(row[3]) if row[3] else 0
                        exam = float(row[4]) if row[4] else 0
                        
                        student = StudentProfile.objects.get(admission_number=admission_no)
                        
                        AcademicRecord.objects.update_or_create(
                            student=student,
                            course=course,
                            term=term,
                            academic_year=term.academic_year,
                            defaults={
                                'continuous_assessment_1': ca1,
                                'continuous_assessment_2': ca2,
                                'continuous_assessment_3': ca3,
                                'exam_score': exam,
                            }
                        )
                        success_count += 1
                    except Exception as e:
                        error_count += 1
                        print(f"Error processing row: {e}")
                
                messages.success(request, f'Successfully uploaded {success_count} records. {error_count} errors.')
                
            elif uploaded_file.name.endswith(('.xlsx', '.xls')):
                import pandas as pd
                df = pd.read_excel(uploaded_file)
                success_count = 0
                error_count = 0
                
                for index, row in df.iterrows():
                    try:
                        admission_no = str(row['Admission No']).strip()
                        ca1 = float(row['CA 1']) if pd.notna(row.get('CA 1')) else 0
                        ca2 = float(row['CA 2']) if pd.notna(row.get('CA 2')) else 0
                        ca3 = float(row['CA 3']) if pd.notna(row.get('CA 3')) else 0
                        exam = float(row['Exam']) if pd.notna(row.get('Exam')) else 0
                        
                        student = StudentProfile.objects.get(admission_number=admission_no)
                        
                        AcademicRecord.objects.update_or_create(
                            student=student,
                            course=course,
                            term=term,
                            academic_year=term.academic_year,
                            defaults={
                                'continuous_assessment_1': ca1,
                                'continuous_assessment_2': ca2,
                                'continuous_assessment_3': ca3,
                                'exam_score': exam,
                            }
                        )
                        success_count += 1
                    except Exception as e:
                        error_count += 1
                        print(f"Error processing row {index}: {e}")
                
                messages.success(request, f'Successfully uploaded {success_count} records. {error_count} errors.')
            else:
                messages.error(request, 'Please upload a CSV or Excel file.')
                
        except Exception as e:
            messages.error(request, f'Error: {str(e)}')
    
    if request.user.role == 'teacher' and hasattr(request.user, 'teacher_profile'):
        context['courses'] = Course.objects.filter(teacher=request.user.teacher_profile)
    else:
        context['courses'] = Course.objects.all()
    
    context['terms'] = Term.objects.all()
    
    return render(request, 'transcripts/upload_marks.html', context)


@login_required
def class_list(request, class_id=None):
    """View and manage class lists"""
    if not (request.user.role in ['teacher', 'admin'] or request.user.is_superuser):
        messages.error(request, 'Permission denied.')
        return redirect('dashboard')
    
    if class_id:
        class_obj = get_object_or_404(Class, id=class_id)
    else:
        class_obj = Class.objects.first()
    
    context = {'class_obj': class_obj, 'user': request.user}
    
    if class_obj:
        students = StudentProfile.objects.filter(current_class=class_obj).select_related('student')
        context['students'] = students
        context['total_students'] = students.count()
        
        current_term = Term.objects.filter(is_current=True).first()
        if current_term:
            context['current_term'] = current_term
            records = AcademicRecord.objects.filter(
                student__in=students,
                term=current_term
            ).select_related('course__subject', 'student__student')
            context['records'] = records
    
    if request.user.role == 'teacher' and hasattr(request.user, 'teacher_profile'):
        context['classes'] = Class.objects.filter(class_teacher=request.user.teacher_profile)
    else:
        context['classes'] = Class.objects.all()
    
    return render(request, 'transcripts/class_list.html', context)


@login_required
def bulk_register_students(request):
    """Bulk register students via CSV"""
    if not (request.user.role in ['admin'] or request.user.is_superuser):
        messages.error(request, 'Permission denied.')
        return redirect('dashboard')
    
    if request.method == 'POST' and request.FILES.get('students_file'):
        uploaded_file = request.FILES['students_file']
        class_id = request.POST.get('class')
        
        try:
            class_obj = Class.objects.get(id=class_id) if class_id else None
            
            if uploaded_file.name.endswith('.csv'):
                text_file = TextIOWrapper(uploaded_file.file, encoding='utf-8')
                reader = csv.reader(text_file)
                next(reader)  # Skip header
                
                success_count = 0
                error_count = 0
                
                for row in reader:
                    try:
                        first_name = row[0].strip()
                        last_name = row[1].strip()
                        email = row[2].strip()
                        admission_no = row[3].strip()
                        gender = row[4].strip().upper()
                        dob = row[5].strip() if len(row) > 5 else '2010-01-01'
                        
                        username = f"{admission_no}_{first_name.lower()}"
                        user_obj = User.objects.create_user(
                            username=username,
                            email=email,
                            password='student123',
                            first_name=first_name,
                            last_name=last_name,
                            role='student'
                        )
                        
                        StudentProfile.objects.create(
                            student=user_obj,
                            admission_number=admission_no,
                            date_of_birth=dob,
                            gender=gender if gender in ['M', 'F'] else 'M',
                            current_class=class_obj
                        )
                        
                        success_count += 1
                    except Exception as e:
                        error_count += 1
                        print(f"Error processing row: {e}")
                
                messages.success(request, f'Successfully registered {success_count} students. {error_count} errors. Default password: student123')
                
        except Exception as e:
            messages.error(request, f'Error: {str(e)}')
    
    context = {
        'classes': Class.objects.all(),
        'user': request.user,
    }
    
    return render(request, 'transcripts/bulk_register.html', context)


@login_required
def enter_marks(request):
    """Manual marks entry interface"""
    if not (request.user.role in ['teacher', 'admin'] or request.user.is_superuser):
        messages.error(request, 'Permission denied.')
        return redirect('dashboard')
    
    context = {'user': request.user}
    
    course_id = request.GET.get('course')
    term_id = request.GET.get('term')
    
    if course_id and term_id:
        course = get_object_or_404(Course, id=course_id)
        term = get_object_or_404(Term, id=term_id)
        
        if course.class_assigned:
            students = StudentProfile.objects.filter(current_class=course.class_assigned)
        else:
            students = StudentProfile.objects.all()
        
        context['course'] = course
        context['term'] = term
        context['students'] = students
        
        if request.method == 'POST':
            success_count = 0
            for student in students:
                try:
                    ca1 = request.POST.get(f'ca1_{student.id}')
                    ca2 = request.POST.get(f'ca2_{student.id}')
                    ca3 = request.POST.get(f'ca3_{student.id}')
                    exam = request.POST.get(f'exam_{student.id}')
                    
                    AcademicRecord.objects.update_or_create(
                        student=student,
                        course=course,
                        term=term,
                        academic_year=term.academic_year,
                        defaults={
                            'continuous_assessment_1': float(ca1) if ca1 else 0,
                            'continuous_assessment_2': float(ca2) if ca2 else 0,
                            'continuous_assessment_3': float(ca3) if ca3 else 0,
                            'exam_score': float(exam) if exam else 0,
                        }
                    )
                    success_count += 1
                except Exception as e:
                    print(f"Error saving {student}: {e}")
            
            messages.success(request, f'Successfully saved marks for {success_count} students.')
            return redirect('enter_marks', course=course_id, term=term_id)
    
    if request.user.role == 'teacher' and hasattr(request.user, 'teacher_profile'):
        context['courses'] = Course.objects.filter(teacher=request.user.teacher_profile)
    else:
        context['courses'] = Course.objects.all()
    
    context['terms'] = Term.objects.all()
    
    return render(request, 'transcripts/enter_marks.html', context)
