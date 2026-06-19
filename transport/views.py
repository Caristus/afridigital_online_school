from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import Bus, Route, StudentTransportAllocation

@login_required
def transport_dashboard(request):
    user = request.user
    context = {'user': user, 'role': user.role}
    
    if user.role == 'student' and hasattr(user, 'student_profile'):
        allocation = StudentTransportAllocation.objects.filter(student=user.student_profile).first()
        context['allocation'] = allocation
    elif user.role == 'transport_manager':
        context['buses'] = Bus.objects.all()
        context['routes'] = Route.objects.all()
    else:
        context['buses'] = Bus.objects.filter(is_active=True)
        context['routes'] = Route.objects.filter(is_active=True)
    
    return render(request, 'transport/dashboard.html', context)
