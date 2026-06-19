from django.db import models
from core.models import BaseModel, Term
from users.models import TeacherProfile

class Subject(BaseModel):
    name = models.CharField(max_length=200)
    code = models.CharField(max_length=50, unique=True)
    description = models.TextField(blank=True, null=True)
    credit_hours = models.IntegerField(default=3)

    class Meta:
        verbose_name = "Subject"
        verbose_name_plural = "Subjects"

    def __str__(self):
        return f"{self.code} - {self.name}"

class Class(BaseModel):
    name = models.CharField(max_length=100)
    grade_level = models.IntegerField()
    capacity = models.IntegerField(default=30)
    class_teacher = models.ForeignKey(TeacherProfile, on_delete=models.SET_NULL, null=True, blank=True)
    academic_year = models.ForeignKey('core.AcademicYear', on_delete=models.CASCADE)

    class Meta:
        verbose_name = "Class"
        verbose_name_plural = "Classes"
        unique_together = ['name', 'academic_year']

    def __str__(self):
        return self.name

class Course(BaseModel):
    title = models.CharField(max_length=200)
    code = models.CharField(max_length=50, unique=True)
    description = models.TextField()
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name='courses')
    teacher = models.ForeignKey(TeacherProfile, on_delete=models.CASCADE, related_name='courses')
    class_assigned = models.ForeignKey(Class, on_delete=models.CASCADE, related_name='courses', null=True, blank=True)
    term = models.ForeignKey(Term, on_delete=models.CASCADE, related_name='courses')
    is_published = models.BooleanField(default=False)

    class Meta:
        verbose_name = "Course"
        verbose_name_plural = "Courses"

    def __str__(self):
        return f"{self.code} - {self.title}"

class Module(BaseModel):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='modules')
    title = models.CharField(max_length=200)
    description = models.TextField()
    order = models.IntegerField(default=0)
    is_published = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Module"
        verbose_name_plural = "Modules"
        ordering = ['order']

    def __str__(self):
        return f"{self.course.code} - {self.title}"

class Lesson(BaseModel):
    module = models.ForeignKey(Module, on_delete=models.CASCADE, related_name='lessons')
    title = models.CharField(max_length=200)
    content = models.TextField()
    video_url = models.URLField(blank=True, null=True)
    order = models.IntegerField(default=0)
    duration_minutes = models.IntegerField(default=0)
    is_published = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Lesson"
        verbose_name_plural = "Lessons"
        ordering = ['order']

    def __str__(self):
        return f"{self.module.title} - {self.title}"

class Enrollment(BaseModel):
    student = models.ForeignKey('users.StudentProfile', on_delete=models.CASCADE, related_name='enrollments')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='enrollments')
    enrolled_date = models.DateField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    completed = models.BooleanField(default=False)

    class Meta:
        verbose_name = "Enrollment"
        verbose_name_plural = "Enrollments"
        unique_together = ['student', 'course']

    def __str__(self):
        return f"{self.student} - {self.course}"

class ProgressTracking(BaseModel):
    enrollment = models.ForeignKey(Enrollment, on_delete=models.CASCADE, related_name='progress')
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE, related_name='progress')
    is_completed = models.BooleanField(default=False)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = "Progress Tracking"
        verbose_name_plural = "Progress Tracking"
        unique_together = ['enrollment', 'lesson']
