from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import Invoice, Payment

@login_required
def finance_dashboard(request):
    user = request.user
    context = {'user': user, 'role': user.role}
    
    if user.role == 'student' and hasattr(user, 'student_profile'):
        invoices = Invoice.objects.filter(student=user.student_profile)
        context['invoices'] = invoices
        context['total_balance'] = sum([inv.balance for inv in invoices])
    elif user.role == 'finance_officer':
        context['invoices'] = Invoice.objects.all()
        context['payments'] = Payment.objects.all()
    else:
        context['invoices'] = Invoice.objects.filter(status='pending')
    
    return render(request, 'finance/dashboard.html', context)
