from django.db import models
from core.models import BaseModel, Term, AcademicYear
from users.models import StudentProfile, TeacherProfile
from academics.models import Course, Subject, Class
from django.utils import timezone
from datetime import date
import uuid

class GPAConfig(BaseModel):
    name = models.CharField(max_length=200)
    academic_year = models.ForeignKey(AcademicYear, on_delete=models.CASCADE)
    scale = models.CharField(max_length=20, choices=[('4.0', '4.0 Scale'), ('5.0', '5.0 Scale'), ('12.0', '12.0 Scale')], default='4.0')
    is_active = models.BooleanField(default=True)
    
    class Meta:
        verbose_name = "GPA Configuration"
        verbose_name_plural = "GPA Configurations"
    
    def __str__(self):
        return f"{self.name} - {self.scale}"

class GradePoint(models.Model):
    gpa_config = models.ForeignKey(GPAConfig, on_delete=models.CASCADE, related_name='grade_points')
    letter_grade = models.CharField(max_length=5)
    min_percentage = models.DecimalField(max_digits=5, decimal_places=2)
    max_percentage = models.DecimalField(max_digits=5, decimal_places=2)
    grade_point = models.DecimalField(max_digits=3, decimal_places=2)
    remarks = models.CharField(max_length=100, blank=True)
    
    class Meta:
        verbose_name = "Grade Point"
        verbose_name_plural = "Grade Points"
        ordering = ['-min_percentage']
    
    def __str__(self):
        return f"{self.letter_grade} - {self.grade_point}"

class AcademicRecord(BaseModel):
    student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE, related_name='academic_records')
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    term = models.ForeignKey(Term, on_delete=models.CASCADE)
    academic_year = models.ForeignKey(AcademicYear, on_delete=models.CASCADE)
    
    # Scores
    continuous_assessment_1 = models.DecimalField(max_digits=5, decimal_places=2, default=0, verbose_name="CA 1")
    continuous_assessment_2 = models.DecimalField(max_digits=5, decimal_places=2, default=0, verbose_name="CA 2")
    continuous_assessment_3 = models.DecimalField(max_digits=5, decimal_places=2, default=0, verbose_name="CA 3")
    exam_score = models.DecimalField(max_digits=5, decimal_places=2, default=0, verbose_name="Exam")
    
    # Calculated fields
    total_ca = models.DecimalField(max_digits=5, decimal_places=2, default=0, editable=False)
    total_score = models.DecimalField(max_digits=5, decimal_places=2, default=0, editable=False)
    percentage = models.DecimalField(max_digits=5, decimal_places=2, default=0, editable=False)
    letter_grade = models.CharField(max_length=5, blank=True)
    grade_point = models.DecimalField(max_digits=3, decimal_places=2, default=0)
    
    # Teacher's input
    teacher_remarks = models.TextField(blank=True, null=True)
    teacher_signature = models.CharField(max_length=200, blank=True, null=True)
    
    class Meta:
        verbose_name = "Academic Record"
        verbose_name_plural = "Academic Records"
        unique_together = ['student', 'course', 'term']
        ordering = ['course__subject__name']
    
    def __str__(self):
        return f"{self.student} - {self.course} - {self.term}"
    
    def save(self, *args, **kwargs):
        # Calculate total CA (average of 3 CAs or sum based on your system)
        self.total_ca = (self.continuous_assessment_1 + 
                        self.continuous_assessment_2 + 
                        self.continuous_assessment_3) / 3
        
        # Calculate total score (40% CA + 60% Exam or adjust as needed)
        self.total_score = (self.total_ca * 0.4) + (self.exam_score * 0.6)
        
        # Calculate percentage
        self.percentage = self.total_score
        
        # Determine letter grade
        if self.total_score >= 80:
            self.letter_grade = 'A'
            self.grade_point = 4.0
        elif self.total_score >= 70:
            self.letter_grade = 'B'
            self.grade_point = 3.0
        elif self.total_score >= 60:
            self.letter_grade = 'C'
            self.grade_point = 2.0
        elif self.total_score >= 50:
            self.letter_grade = 'D'
            self.grade_point = 1.0
        else:
            self.letter_grade = 'F'
            self.grade_point = 0.0
        
        super().save(*args, **kwargs)

class Transcript(BaseModel):
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('pending_approval', 'Pending Approval'),
        ('approved', 'Approved'),
        ('published', 'Published'),
    ]
    
    student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE, related_name='transcripts')
    academic_year = models.ForeignKey(AcademicYear, on_delete=models.CASCADE)
    term = models.ForeignKey(Term, on_delete=models.CASCADE)
    
    # Calculated results
    total_marks = models.DecimalField(max_digits=6, decimal_places=2, default=0)
    average_marks = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    gpa = models.DecimalField(max_digits=4, decimal_places=2, default=0)
    class_position = models.IntegerField(null=True, blank=True)
    total_students_in_class = models.IntegerField(null=True, blank=True)
    grade_position = models.IntegerField(null=True, blank=True)
    total_students_in_grade = models.IntegerField(null=True, blank=True)
    
    # Attendance
    days_present = models.IntegerField(default=0)
    days_absent = models.IntegerField(default=0)
    attendance_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    
    # Behavioral and comments
    conduct_grade = models.CharField(max_length=5, default='A')
    general_remarks = models.TextField(blank=True, null=True)
    class_teacher_remarks = models.TextField(blank=True, null=True)
    principal_remarks = models.TextField(blank=True, null=True)
    parent_signature = models.CharField(max_length=200, blank=True, null=True)
    parent_date = models.DateField(null=True, blank=True)
    
    # Status and tracking
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    generated_date = models.DateTimeField(auto_now_add=True)
    approved_by = models.ForeignKey(TeacherProfile, on_delete=models.SET_NULL, null=True, blank=True, related_name='approved_transcripts')
    approved_date = models.DateTimeField(null=True, blank=True)
    pdf_file = models.FileField(upload_to='transcripts/pdfs/', blank=True, null=True)
    
    class Meta:
        verbose_name = "Transcript"
        verbose_name_plural = "Transcripts"
        unique_together = ['student', 'academic_year', 'term']
        ordering = ['-academic_year__name', '-term__name']
    
    def __str__(self):
        return f"Transcript - {self.student} - {self.term} {self.academic_year.name}"
    
    def calculate_results(self):
        """Calculate all transcript metrics"""
        records = AcademicRecord.objects.filter(
            student=self.student,
            term=self.term,
            academic_year=self.academic_year
        )
        
        if records.exists():
            self.total_marks = sum([r.total_score for r in records])
            self.average_marks = self.total_marks / records.count()
            
            # Calculate GPA
            total_points = sum([r.grade_point * r.course.credit_hours for r in records])
            total_credits = sum([r.course.credit_hours for r in records])
            self.gpa = total_points / total_credits if total_credits > 0 else 0
        
        self.save()

class SubjectPerformance(BaseModel):
    """Track subject-wise performance over time"""
    student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE, related_name='subject_performances')
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    academic_year = models.ForeignKey(AcademicYear, on_delete=models.CASCADE)
    
    term1_score = models.DecimalField(max_digits=5, decimal_places=2, default=0, null=True, blank=True)
    term2_score = models.DecimalField(max_digits=5, decimal_places=2, default=0, null=True, blank=True)
    term3_score = models.DecimalField(max_digits=5, decimal_places=2, default=0, null=True, blank=True)
    average_score = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    trend = models.CharField(max_length=20, choices=[
        ('improving', 'Improving'),
        ('declining', 'Declining'),
        ('stable', 'Stable')
    ], default='stable')
    
    class Meta:
        verbose_name = "Subject Performance"
        verbose_name_plural = "Subject Performances"
        unique_together = ['student', 'subject', 'academic_year']
    
    def __str__(self):
        return f"{self.student} - {self.subject}"

class ReportCardTemplate(BaseModel):
    """Customizable report card templates"""
    name = models.CharField(max_length=200)
    school_name = models.CharField(max_length=300)
    school_address = models.TextField()
    school_phone = models.CharField(max_length=50)
    school_email = models.EmailField()
    school_logo = models.ImageField(upload_to='school_logos/', blank=True, null=True)
    
    term_info = models.TextField(help_text="Term information text")
    academic_year_info = models.TextField(help_text="Academic year information")
    
    # Customization options
    show_grading_scale = models.BooleanField(default=True)
    show_attendance = models.BooleanField(default=True)
    show_conduct = models.BooleanField(default=True)
    show_remarks = models.BooleanField(default=True)
    show_signature_lines = models.BooleanField(default=True)
    
    is_default = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        verbose_name = "Report Card Template"
        verbose_name_plural = "Report Card Templates"
    
    def __str__(self):
        return self.name

class BehavioralReport(BaseModel):
    """Track student behavior and conduct"""
    student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE, related_name='behavioral_reports')
    term = models.ForeignKey(Term, on_delete=models.CASCADE)
    academic_year = models.ForeignKey(AcademicYear, on_delete=models.CASCADE)
    
    # Behavioral aspects (1-5 scale or A-E)
    punctuality = models.CharField(max_length=5, default='A')
    attendance = models.CharField(max_length=5, default='A')
    neatness = models.CharField(max_length=5, default='A')
    respect = models.CharField(max_length=5, default='A')
    participation = models.CharField(max_length=5, default='A')
    homework_completion = models.CharField(max_length=5, default='A')
    teamwork = models.CharField(max_length=5, default='A')
    leadership = models.CharField(max_length=5, default='A')
    
    # Overall
    overall_conduct = models.CharField(max_length=5, default='A')
    teacher_comments = models.TextField(blank=True)
    
    reported_by = models.ForeignKey(TeacherProfile, on_delete=models.SET_NULL, null=True)
    reported_date = models.DateField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Behavioral Report"
        verbose_name_plural = "Behavioral Reports"
        unique_together = ['student', 'term', 'academic_year']
    
    def __str__(self):
        return f"Behavior - {self.student} - {self.term}"
