from django.db import models
from core.models import BaseModel, Term
from academics.models import Course
from users.models import StudentProfile, TeacherProfile

class Assessment(BaseModel):
    ASSESSMENT_TYPE_CHOICES = [
        ('quiz', 'Quiz'), ('exam', 'Exam'), ('assignment', 'Assignment'), ('test', 'Test'),
    ]
    title = models.CharField(max_length=200)
    description = models.TextField()
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='assessments')
    assessment_type = models.CharField(max_length=20, choices=ASSESSMENT_TYPE_CHOICES)
    total_marks = models.DecimalField(max_digits=5, decimal_places=2)
    passing_marks = models.DecimalField(max_digits=5, decimal_places=2)
    duration_minutes = models.IntegerField(default=0)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    is_published = models.BooleanField(default=False)
    created_by = models.ForeignKey(TeacherProfile, on_delete=models.CASCADE)
    term = models.ForeignKey(Term, on_delete=models.CASCADE, related_name='assessments')

    class Meta:
        verbose_name = "Assessment"
        verbose_name_plural = "Assessments"

    def __str__(self):
        return f"{self.title} - {self.course.code}"

class Question(BaseModel):
    QUESTION_TYPE_CHOICES = [
        ('multiple_choice', 'Multiple Choice'), ('true_false', 'True/False'),
        ('short_answer', 'Short Answer'), ('essay', 'Essay'),
    ]
    assessment = models.ForeignKey(Assessment, on_delete=models.CASCADE, related_name='questions', null=True, blank=True)
    question_text = models.TextField()
    question_type = models.CharField(max_length=20, choices=QUESTION_TYPE_CHOICES)
    marks = models.DecimalField(max_digits=5, decimal_places=2, default=1)
    order = models.IntegerField(default=0)

    class Meta:
        verbose_name = "Question"
        verbose_name_plural = "Questions"
        ordering = ['order']

    def __str__(self):
        return f"{self.question_text[:50]}..."

class Answer(BaseModel):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='answers')
    answer_text = models.TextField()
    is_correct = models.BooleanField(default=False)
    order = models.IntegerField(default=0)

    class Meta:
        verbose_name = "Answer"
        verbose_name_plural = "Answers"
        ordering = ['order']

class Submission(BaseModel):
    student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE, related_name='submissions')
    assessment = models.ForeignKey(Assessment, on_delete=models.CASCADE, related_name='submissions')
    submitted_at = models.DateTimeField(auto_now_add=True)
    text_answer = models.TextField(blank=True, null=True)
    file_upload = models.FileField(upload_to='submissions/', blank=True, null=True)

    class Meta:
        verbose_name = "Submission"
        verbose_name_plural = "Submissions"
        unique_together = ['student', 'assessment']

    def __str__(self):
        return f"{self.student} - {self.assessment.title}"

class Grade(BaseModel):
    submission = models.OneToOneField(Submission, on_delete=models.CASCADE, related_name='grade')
    marks_obtained = models.DecimalField(max_digits=5, decimal_places=2)
    percentage = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    grade_letter = models.CharField(max_length=5, null=True, blank=True)
    feedback = models.TextField(blank=True, null=True)
    graded_by = models.ForeignKey(TeacherProfile, on_delete=models.SET_NULL, null=True, blank=True)
    is_graded = models.BooleanField(default=False)

    class Meta:
        verbose_name = "Grade"
        verbose_name_plural = "Grades"

    def save(self, *args, **kwargs):
        if self.marks_obtained and self.submission.assessment.total_marks:
            self.percentage = (self.marks_obtained / self.submission.assessment.total_marks) * 100
        super().save(*args, **kwargs)
