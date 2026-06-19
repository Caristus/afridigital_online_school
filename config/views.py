from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.db import models
from users.models import User, StudentProfile, TeacherProfile, ParentProfile
from academics.models import Course, Enrollment
from finance.models import Invoice, Payment
from library.models import Book
from transport.models import Bus

def is_admin(user):
    return user.is_authenticated and (user.is_superuser or user.role == 'admin')

def custom_login(request):
    if request.user.is_authenticated and (request.user.is_superuser or request.user.role == 'admin'):
        return redirect('custom_admin_dashboard')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        
        if user is not None and (user.is_superuser or user.role == 'admin'):
            login(request, user)
            messages.success(request, f'Welcome back, {user.get_full_name()}!')
            return redirect('custom_admin_dashboard')
        else:
            messages.error(request, 'Invalid credentials or insufficient permissions.')
    
    return render(request, 'custom_admin/login.html')

@login_required
@user_passes_test(is_admin)
def custom_admin_dashboard(request):
    context = {
        'total_users': User.objects.count(),
        'total_students': StudentProfile.objects.count(),
        'total_teachers': TeacherProfile.objects.count(),
        'total_parents': ParentProfile.objects.count(),
        'total_courses': Course.objects.count(),
        'total_enrollments': Enrollment.objects.filter(is_active=True).count(),
        'pending_invoices': Invoice.objects.filter(status='pending').count(),
        'total_revenue': Invoice.objects.filter(status='paid').aggregate(total=models.Sum('amount_paid'))['total'] or 0,
        'available_books': Book.objects.filter(available_copies__gt=0).count(),
        'active_buses': Bus.objects.filter(is_active=True).count(),
        'recent_users': User.objects.order_by('-date_joined')[:5],
        'recent_courses': Course.objects.order_by('-created_at')[:5],
    }
    return render(request, 'custom_admin/dashboard.html')

@login_required
@user_passes_test(is_admin)
def user_management(request):
    users = User.objects.all()
    if request.GET.get('role'):
        users = users.filter(role=request.GET.get('role'))
    if request.GET.get('search'):
        users = users.filter(
            models.Q(first_name__icontains=request.GET.get('search')) |
            models.Q(last_name__icontains=request.GET.get('search')) |
            models.Q(email__icontains=request.GET.get('search'))
        )
    return render(request, 'custom_admin/user_management.html', {'users': users})

@login_required
@user_passes_test(is_admin)
def course_management(request):
    courses = Course.objects.all().select_related('teacher', 'subject')
    return render(request, 'custom_admin/course_management.html', {'courses': courses})

@login_required
@user_passes_test(is_admin)
def finance_management(request):
    invoices = Invoice.objects.all().select_related('student', 'fee_structure')
    payments = Payment.objects.all().select_related('invoice')[:50]
    total_revenue = Invoice.objects.filter(status='paid').aggregate(total=models.Sum('amount_paid'))['total'] or 0
    pending_amount = Invoice.objects.filter(status='pending').aggregate(total=models.Sum('balance'))['total'] or 0
    return render(request, 'custom_admin/finance_management.html', {
        'invoices': invoices,
        'payments': payments,
        'total_revenue': total_revenue,
        'pending_amount': pending_amount,
    })

@login_required
@user_passes_test(is_admin)
def custom_logout(request):
    logout(request)
    messages.success(request, 'You have been logged out successfully.')
    return redirect('custom_admin_login')
