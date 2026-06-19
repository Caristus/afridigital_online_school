from django.contrib import admin
from .models import Subject, Class, Course, Module, Lesson, Enrollment, ProgressTracking

@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'credit_hours')
    search_fields = ('name', 'code')

@admin.register(Class)
class ClassAdmin(admin.ModelAdmin):
    list_display = ('name', 'grade_level', 'class_teacher', 'academic_year')
    list_filter = ('grade_level', 'academic_year')
    search_fields = ('name',)
    # Make it easier to select teachers in the dropdown
    raw_id_fields = ('class_teacher',)

@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ('code', 'title', 'teacher', 'subject', 'class_assigned', 'is_published')
    list_filter = ('is_published', 'term', 'subject')
    search_fields = ('title', 'code')
    raw_id_fields = ('teacher', 'class_assigned')

@admin.register(Module)
class ModuleAdmin(admin.ModelAdmin):
    list_display = ('title', 'course', 'order', 'is_published')
    list_filter = ('course', 'is_published')

@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    list_display = ('title', 'module', 'order', 'duration_minutes')
    list_filter = ('module', 'is_published')

@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    list_display = ('student', 'course', 'enrolled_date', 'is_active')
    list_filter = ('is_active', 'completed')
    raw_id_fields = ('student', 'course')

@admin.register(ProgressTracking)
class ProgressTrackingAdmin(admin.ModelAdmin):
    list_display = ('enrollment', 'lesson', 'is_completed')
    list_filter = ('is_completed',)
    raw_id_fields = ('enrollment', 'lesson')
