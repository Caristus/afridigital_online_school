from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.http import HttpResponse
from users.models import User, StudentProfile, TeacherProfile, AdminProfile, SystemAdminProfile, LibrarianProfile, FinanceProfile, TransportProfile
from academics.models import Subject, Class, Course
from core.models import AcademicYear, Term
from transcripts.models import AcademicRecord
import csv
from io import TextIOWrapper
from datetime import datetime
import json

def is_system_admin(user):
    return user.is_authenticated and user.role == 'system_admin' and user.is_superuser

def user_login(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            messages.success(request, f'Welcome back, {user.get_full_name()}!')
            return redirect('dashboard')
        else:
            messages.error(request, 'Invalid email or password.')
    
    return render(request, 'registration/login.html')

@login_required
def dashboard(request):
    user = request.user
    context = {
        'user': user,
        'role': user.role,
    }
    
    try:
        if user.role == 'student' and hasattr(user, 'student_profile'):
            context['enrollments'] = user.student_profile.enrollments.filter(is_active=True).count()
        elif user.role == 'teacher' and hasattr(user, 'teacher_profile'):
            context['courses'] = user.teacher_profile.courses.count()
        elif user.role == 'parent' and hasattr(user, 'parent_profile'):
            context['children'] = user.children.count()
        elif user.role == 'librarian' and hasattr(user, 'librarian_profile'):
            context['books'] = 0
        elif user.role == 'finance_officer' and hasattr(user, 'finance_profile'):
            context['invoices'] = 0
        elif user.role == 'transport_manager' and hasattr(user, 'transport_profile'):
            context['buses'] = 0
        elif user.role == 'system_admin':
            context['total_users'] = User.objects.count()
            context['system_status'] = 'Online'
            context['last_backup'] = 'Today'
    except Exception as e:
        pass

    return render(request, 'dashboard.html', context)

@login_required
@user_passes_test(is_system_admin)
def bulk_upload_subjects(request):
    if request.method == 'POST' and request.FILES.get('subjects_file'):
        uploaded_file = request.FILES['subjects_file']
        
        try:
            if uploaded_file.name.endswith('.csv'):
                text_file = TextIOWrapper(uploaded_file.file, encoding='utf-8')
                reader = csv.reader(text_file)
                next(reader, None)
                
                success_count = 0
                error_count = 0
                
                for row in reader:
                    try:
                        if len(row) >= 2:
                            name = row[0].strip()
                            code = row[1].strip()
                            credit_hours = int(row[2]) if len(row) > 2 and row[2] else 3
                            description = row[3].strip() if len(row) > 3 else ''
                            
                            Subject.objects.update_or_create(
                                code=code,
                                defaults={
                                    'name': name,
                                    'credit_hours': credit_hours,
                                    'description': description
                                }
                            )
                            success_count += 1
                    except Exception as e:
                        error_count += 1
                
                messages.success(request, f'Successfully uploaded {success_count} subjects. {error_count} errors.')
                return redirect('bulk_upload_subjects')
                
            elif uploaded_file.name.endswith(('.xlsx', '.xls')):
                import pandas as pd
                df = pd.read_excel(uploaded_file)
                success_count = 0
                error_count = 0
                
                for index, row in df.iterrows():
                    try:
                        name = str(row['Name']).strip()
                        code = str(row['Code']).strip()
                        credit_hours = int(row['Credit Hours']) if pd.notna(row.get('Credit Hours')) else 3
                        description = str(row.get('Description', '')).strip() if pd.notna(row.get('Description')) else ''
                        
                        Subject.objects.update_or_create(
                            code=code,
                            defaults={
                                'name': name,
                                'credit_hours': credit_hours,
                                'description': description
                            }
                        )
                        success_count += 1
                    except Exception as e:
                        error_count += 1
                
                messages.success(request, f'Successfully uploaded {success_count} subjects. {error_count} errors.')
                return redirect('bulk_upload_subjects')
            else:
                messages.error(request, 'Please upload a CSV or Excel file.')
        except Exception as e:
            messages.error(request, f'Error: {str(e)}')
    
    return render(request, 'users/bulk_upload_subjects.html')

@login_required
@user_passes_test(is_system_admin)
def bulk_upload_teachers(request):
    if request.method == 'POST' and request.FILES.get('teachers_file'):
        uploaded_file = request.FILES['teachers_file']
        
        try:
            if uploaded_file.name.endswith('.csv'):
                text_file = TextIOWrapper(uploaded_file.file, encoding='utf-8')
                reader = csv.reader(text_file)
                next(reader, None)
                
                success_count = 0
                error_count = 0
                
                for row in reader:
                    try:
                        if len(row) >= 4:
                            first_name = row[0].strip()
                            last_name = row[1].strip()
                            email = row[2].strip()
                            employee_id = row[3].strip()
                            qualification = row[4].strip() if len(row) > 4 else ''
                            specialization = row[5].strip() if len(row) > 5 else ''
                            
                            username = f"teacher_{employee_id}"
                            user, created = User.objects.get_or_create(
                                email=email,
                                defaults={
                                    'username': username,
                                    'first_name': first_name,
                                    'last_name': last_name,
                                    'role': 'teacher',
                                    'is_staff': True
                                }
                            )
                            
                            if created:
                                user.set_password('teacher123')
                                user.save()
                            
                            TeacherProfile.objects.update_or_create(
                                teacher=user,
                                defaults={
                                    'employee_id': employee_id,
                                    'qualification': qualification,
                                    'specialization': specialization
                                }
                            )
                            success_count += 1
                    except Exception as e:
                        error_count += 1
                
                messages.success(request, f'Successfully uploaded {success_count} teachers. {error_count} errors. Default password: teacher123')
                return redirect('bulk_upload_teachers')
        except Exception as e:
            messages.error(request, f'Error: {str(e)}')
    
    return render(request, 'users/bulk_upload_teachers.html')

@login_required
@user_passes_test(is_system_admin)
def bulk_upload_classes(request):
    if request.method == 'POST' and request.FILES.get('classes_file'):
        uploaded_file = request.FILES['classes_file']
        academic_year_id = request.POST.get('academic_year')
        
        try:
            academic_year = AcademicYear.objects.get(id=academic_year_id) if academic_year_id else AcademicYear.objects.filter(is_current=True).first()
            
            if not academic_year:
                messages.error(request, 'Please select or create an academic year first.')
                return redirect('bulk_upload_classes')
            
            if uploaded_file.name.endswith('.csv'):
                text_file = TextIOWrapper(uploaded_file.file, encoding='utf-8')
                reader = csv.reader(text_file)
                next(reader, None)
                
                success_count = 0
                error_count = 0
                
                for row in reader:
                    try:
                        if len(row) >= 2:
                            name = row[0].strip()
                            grade_level = int(row[1])
                            capacity = int(row[2]) if len(row) > 2 and row[2] else 30
                            
                            Class.objects.update_or_create(
                                name=name,
                                academic_year=academic_year,
                                defaults={
                                    'grade_level': grade_level,
                                    'capacity': capacity
                                }
                            )
                            success_count += 1
                    except Exception as e:
                        error_count += 1
                
                messages.success(request, f'Successfully uploaded {success_count} classes. {error_count} errors.')
                return redirect('bulk_upload_classes')
        except Exception as e:
            messages.error(request, f'Error: {str(e)}')
    
    context = {
        'academic_years': AcademicYear.objects.all()
    }
    return render(request, 'users/bulk_upload_classes.html', context)

@login_required
@user_passes_test(is_system_admin)
def bulk_upload_classlist(request):
    if request.method == 'POST' and request.FILES.get('classlist_file'):
        uploaded_file = request.FILES['classlist_file']
        class_id = request.POST.get('class')
        
        try:
            class_obj = Class.objects.get(id=class_id) if class_id else None
            
            if not class_obj:
                messages.error(request, 'Please select a class.')
                return redirect('bulk_upload_classlist')
            
            if uploaded_file.name.endswith('.csv'):
                text_file = TextIOWrapper(uploaded_file.file, encoding='utf-8')
                reader = csv.reader(text_file)
                next(reader, None)
                
                success_count = 0
                error_count = 0
                
                for row in reader:
                    try:
                        if len(row) >= 4:
                            first_name = row[0].strip()
                            last_name = row[1].strip()
                            email = row[2].strip()
                            admission_number = row[3].strip()
                            gender = row[4].strip().upper() if len(row) > 4 else 'M'
                            dob = row[5].strip() if len(row) > 5 and row[5] else '2010-01-01'
                            
                            username = f"student_{admission_number}"
                            user, created = User.objects.get_or_create(
                                email=email,
                                defaults={
                                    'username': username,
                                    'first_name': first_name,
                                    'last_name': last_name,
                                    'role': 'student'
                                }
                            )
                            
                            if created:
                                user.set_password('student123')
                                user.save()
                            
                            StudentProfile.objects.update_or_create(
                                student=user,
                                defaults={
                                    'admission_number': admission_number,
                                    'date_of_birth': dob,
                                    'gender': gender if gender in ['M', 'F', 'O'] else 'M',
                                    'current_class': class_obj
                                }
                            )
                            success_count += 1
                    except Exception as e:
                        error_count += 1
                
                messages.success(request, f'Successfully uploaded {success_count} students. {error_count} errors. Default password: student123')
                return redirect('bulk_upload_classlist')
        except Exception as e:
            messages.error(request, f'Error: {str(e)}')
    
    context = {
        'classes': Class.objects.all()
    }
    return render(request, 'users/bulk_upload_classlist.html', context)

@login_required
@user_passes_test(is_system_admin)
def bulk_upload_marks(request):
    if request.method == 'POST' and request.FILES.get('marks_file'):
        uploaded_file = request.FILES['marks_file']
        course_id = request.POST.get('course')
        term_id = request.POST.get('term')
        
        try:
            course = Course.objects.get(id=course_id) if course_id else None
            term = Term.objects.get(id=term_id) if term_id else Term.objects.filter(is_current=True).first()
            
            if not course:
                messages.error(request, 'Please select a course.')
                return redirect('bulk_upload_marks')
            
            if not term:
                messages.error(request, 'Please select a term.')
                return redirect('bulk_upload_marks')
            
            if uploaded_file.name.endswith('.csv'):
                text_file = TextIOWrapper(uploaded_file.file, encoding='utf-8')
                reader = csv.reader(text_file)
                next(reader, None)
                
                success_count = 0
                error_count = 0
                
                for row in reader:
                    try:
                        if len(row) >= 5:
                            admission_number = row[0].strip()
                            ca1 = float(row[1]) if row[1] else 0
                            ca2 = float(row[2]) if row[2] else 0
                            ca3 = float(row[3]) if row[3] else 0
                            exam = float(row[4]) if row[4] else 0
                            
                            student = StudentProfile.objects.get(admission_number=admission_number)
                            
                            AcademicRecord.objects.update_or_create(
                                student=student,
                                course=course,
                                term=term,
                                academic_year=term.academic_year,
                                defaults={
                                    'continuous_assessment_1': ca1,
                                    'continuous_assessment_2': ca2,
                                    'continuous_assessment_3': ca3,
                                    'exam_score': exam
                                }
                            )
                            success_count += 1
                    except Exception as e:
                        error_count += 1
                
                messages.success(request, f'Successfully uploaded {success_count} marks. {error_count} errors.')
                return redirect('bulk_upload_marks')
        except Exception as e:
            messages.error(request, f'Error: {str(e)}')
    
    context = {
        'courses': Course.objects.all(),
        'terms': Term.objects.all()
    }
    return render(request, 'users/bulk_upload_marks.html', context)

@login_required
@user_passes_test(is_system_admin)
def download_template(request, template_type):
    templates = {
        'subjects': 'Name,Code,Credit Hours,Description\nMathematics,MATH101,3,Introduction to Mathematics\nEnglish,ENG101,3,English Literature and Composition',
        'teachers': 'First Name,Last Name,Email,Employee ID,Qualification,Specialization\nJohn,Smith,john.smith@afridigital.com,TCH001,Bachelor of Education,Mathematics',
        'classes': 'Class Name,Grade Level,Capacity\nGrade 10A,10,30\nGrade 10B,10,30',
        'classlist': 'First Name,Last Name,Email,Admission Number,Gender,Date of Birth\nAlice,Johnson,alice@student.com,STD001,F,2008-05-15',
        'marks': 'Admission Number,CA 1,CA 2,CA 3,Exam\nSTD001,75,80,78,85\nSTD002,65,70,68,75'
    }
    
    if template_type in templates:
        response = HttpResponse(templates[template_type], content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="{template_type}_template.csv"'
        return response
    
    return redirect('dashboard')
