from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Assessment, Submission, Grade
from .forms import SubmissionForm

@login_required
def assessments_dashboard(request):
    user = request.user
    context = {'user': user, 'role': user.role}
    
    if user.role == 'student' and hasattr(user, 'student_profile'):
        submissions = Submission.objects.filter(student=user.student_profile)
        context['submissions'] = submissions
        context['grades'] = Grade.objects.filter(submission__in=submissions)
        context['available_assessments'] = Assessment.objects.filter(
            is_published=True,
            course__enrollments__student=user.student_profile
        ).exclude(
            id__in=submissions.values_list('assessment_id', flat=True)
        )
    elif user.role == 'teacher' and hasattr(user, 'teacher_profile'):
        context['assessments'] = Assessment.objects.filter(created_by=user.teacher_profile)
        context['pending_submissions'] = Submission.objects.filter(
            assessment__created_by=user.teacher_profile,
            grade__isnull=True
        )
    else:
        context['assessments'] = Assessment.objects.filter(is_published=True)
    
    return render(request, 'assessments/dashboard.html', context)

@login_required
def submit_assessment(request, assessment_id):
    assessment = get_object_or_404(Assessment, id=assessment_id)
    
    if request.user.role != 'student' or not hasattr(request.user, 'student_profile'):
        messages.error(request, 'Only students can submit assessments.')
        return redirect('assessments_dashboard')
    
    # Check if already submitted
    if Submission.objects.filter(student=request.user.student_profile, assessment=assessment).exists():
        messages.warning(request, 'You have already submitted this assessment.')
        return redirect('assessments_dashboard')
    
    if request.method == 'POST':
        form = SubmissionForm(request.POST, request.FILES)
        if form.is_valid():
            submission = form.save(commit=False)
            submission.student = request.user.student_profile
            submission.assessment = assessment
            submission.save()
            messages.success(request, 'Assessment submitted successfully!')
            return redirect('assessments_dashboard')
    else:
        form = SubmissionForm()
    
    return render(request, 'assessments/submit.html', {
        'form': form,
        'assessment': assessment
    })

@login_required
def view_grade(request, submission_id):
    submission = get_object_or_404(Submission, id=submission_id)
    
    # Check permissions
    if request.user.role == 'student':
        if submission.student.student != request.user:
            messages.error(request, 'You do not have permission to view this grade.')
            return redirect('assessments_dashboard')
    elif request.user.role == 'teacher':
        if submission.assessment.created_by.teacher != request.user:
            messages.error(request, 'You do not have permission to view this grade.')
            return redirect('assessments_dashboard')
    
    grade = Grade.objects.filter(submission=submission).first()
    
    return render(request, 'assessments/view_grade.html', {
        'submission': submission,
        'grade': grade
    })
