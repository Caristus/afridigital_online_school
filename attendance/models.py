from django.db import models
from django.utils import timezone
from core.models import BaseModel, Term
from academics.models import Class, Course
from users.models import StudentProfile, TeacherProfile

class AttendanceSession(BaseModel):
    session_type = models.CharField(max_length=20, choices=[('daily', 'Daily'), ('lesson', 'Lesson')])
    class_assigned = models.ForeignKey(Class, on_delete=models.CASCADE, related_name='attendance_sessions')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='attendance_sessions', null=True, blank=True)
    date = models.DateField(default=timezone.now)
    term = models.ForeignKey(Term, on_delete=models.CASCADE, related_name='attendance_sessions')
    created_by = models.ForeignKey(TeacherProfile, on_delete=models.CASCADE)

    class Meta:
        verbose_name = "Attendance Session"
        verbose_name_plural = "Attendance Sessions"
        unique_together = ['class_assigned', 'date', 'session_type']

    def __str__(self):
        return f"{self.class_assigned} - {self.date}"

class AttendanceRecord(BaseModel):
    STATUS_CHOICES = [('present', 'Present'), ('absent', 'Absent'), ('late', 'Late'), ('excused', 'Excused')]
    session = models.ForeignKey(AttendanceSession, on_delete=models.CASCADE, related_name='records')
    student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE, related_name='attendance_records')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='present')
    remarks = models.TextField(blank=True, null=True)

    class Meta:
        verbose_name = "Attendance Record"
        verbose_name_plural = "Attendance Records"
        unique_together = ['session', 'student']

    def __str__(self):
        return f"{self.student} - {self.status}"
