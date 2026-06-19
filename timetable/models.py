from django.db import models
from core.models import BaseModel, Term, AcademicYear
from academics.models import Class, Subject
from users.models import TeacherProfile

class Room(BaseModel):
    name = models.CharField(max_length=100)
    capacity = models.IntegerField()
    building = models.CharField(max_length=100, blank=True, null=True)

    class Meta:
        verbose_name = "Room"
        verbose_name_plural = "Rooms"

    def __str__(self):
        return f"{self.name} (Cap: {self.capacity})"

class Timetable(BaseModel):
    name = models.CharField(max_length=200)
    class_assigned = models.ForeignKey(Class, on_delete=models.CASCADE, related_name='timetables')
    term = models.ForeignKey(Term, on_delete=models.CASCADE, related_name='timetables')
    academic_year = models.ForeignKey(AcademicYear, on_delete=models.CASCADE)
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Timetable"
        verbose_name_plural = "Timetables"

    def __str__(self):
        return f"{self.name} - {self.class_assigned}"

class ClassSession(BaseModel):
    DAY_CHOICES = [
        ('Monday', 'Monday'), ('Tuesday', 'Tuesday'), ('Wednesday', 'Wednesday'),
        ('Thursday', 'Thursday'), ('Friday', 'Friday'), ('Saturday', 'Saturday')
    ]
    
    timetable = models.ForeignKey(Timetable, on_delete=models.CASCADE, related_name='sessions')
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    teacher = models.ForeignKey(TeacherProfile, on_delete=models.CASCADE)
    room = models.ForeignKey(Room, on_delete=models.SET_NULL, null=True, blank=True)
    day = models.CharField(max_length=20, choices=DAY_CHOICES)
    start_time = models.TimeField()
    end_time = models.TimeField()
    period_name = models.CharField(max_length=50, blank=True, help_text="e.g., Period 1, Morning Break")

    class Meta:
        verbose_name = "Class Session"
        verbose_name_plural = "Class Sessions"
        ordering = ['day', 'start_time']

    def __str__(self):
        return f"{self.subject} - {self.day} {self.start_time}"

class SubjectAllocation(BaseModel):
    class_assigned = models.ForeignKey(Class, on_delete=models.CASCADE, related_name='subject_allocations')
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    teacher = models.ForeignKey(TeacherProfile, on_delete=models.CASCADE)
    term = models.ForeignKey(Term, on_delete=models.CASCADE)
    periods_per_week = models.IntegerField(default=3)

    class Meta:
        verbose_name = "Subject Allocation"
        verbose_name_plural = "Subject Allocations"
        unique_together = ['class_assigned', 'subject', 'term']

    def __str__(self):
        return f"{self.class_assigned} - {self.subject} ({self.teacher})"
