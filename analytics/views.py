from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import PerformanceReport, FinancialReport

@login_required
def analytics_dashboard(request):
    user = request.user
    context = {'user': user, 'role': user.role}
    
    context['performance_reports'] = PerformanceReport.objects.all()[:5]
    context['financial_reports'] = FinancialReport.objects.all()[:5]
    
    return render(request, 'analytics/dashboard.html', context)
