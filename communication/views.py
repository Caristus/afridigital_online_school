from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import Message, Notification, Announcement

@login_required
def communication_dashboard(request):
    user = request.user
    context = {'user': user, 'role': user.role}
    
    context['messages'] = Message.objects.filter(recipient=user)[:10]
    context['notifications'] = Notification.objects.filter(recipient=user)[:10]
    context['announcements'] = Announcement.objects.filter(is_published=True)[:5]
    
    return render(request, 'communication/dashboard.html', context)
