from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import Book, BorrowRecord

@login_required
def library_dashboard(request):
    user = request.user
    context = {'user': user, 'role': user.role}
    
    if user.role == 'student' and hasattr(user, 'student_profile'):
        context['borrowed_books'] = BorrowRecord.objects.filter(student=user.student_profile, is_returned=False)
        context['books'] = Book.objects.filter(available_copies__gt=0)
    elif user.role == 'librarian':
        context['books'] = Book.objects.all()
        context['borrow_records'] = BorrowRecord.objects.all()
    else:
        context['books'] = Book.objects.filter(available_copies__gt=0)
    
    return render(request, 'library/dashboard.html', context)
