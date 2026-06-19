from django.contrib import admin
from .models import Room, Timetable, ClassSession, SubjectAllocation

@admin.register(Room)
class RoomAdmin(admin.ModelAdmin):
    list_display = ('name', 'capacity', 'building')
    search_fields = ('name', 'building')

@admin.register(Timetable)
class TimetableAdmin(admin.ModelAdmin):
    list_display = ('name', 'class_assigned', 'term', 'is_active')
    list_filter = ('term', 'is_active')
    raw_id_fields = ('class_assigned',)

@admin.register(ClassSession)
class ClassSessionAdmin(admin.ModelAdmin):
    list_display = ('timetable', 'subject', 'teacher', 'day', 'start_time', 'end_time')
    list_filter = ('day', 'timetable')
    raw_id_fields = ('teacher', 'room', 'timetable')

@admin.register(SubjectAllocation)
class SubjectAllocationAdmin(admin.ModelAdmin):
    list_display = ('class_assigned', 'subject', 'teacher', 'term', 'periods_per_week')
    list_filter = ('term', 'subject')
    search_fields = ('class_assigned__name', 'subject__name')
    raw_id_fields = ('class_assigned', 'subject', 'teacher')
