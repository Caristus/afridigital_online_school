from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import (
    User, StudentProfile, TeacherProfile, ParentProfile, 
    AdminProfile, LibrarianProfile, FinanceProfile, TransportProfile,
    SystemAdminProfile
)

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ('email', 'username', 'role', 'first_name', 'last_name', 'is_staff')
    list_filter = ('role', 'is_staff', 'is_active')
    fieldsets = UserAdmin.fieldsets + (
        ('Additional Info', {'fields': ('role', 'phone', 'profile_picture')}),
    )

@admin.register(StudentProfile)
class StudentProfileAdmin(admin.ModelAdmin):
    list_display = ('student', 'admission_number', 'current_class', 'gender')
    search_fields = ('admission_number', 'student__first_name')

@admin.register(TeacherProfile)
class TeacherProfileAdmin(admin.ModelAdmin):
    list_display = ('teacher', 'employee_id', 'specialization')

@admin.register(ParentProfile)
class ParentProfileAdmin(admin.ModelAdmin):
    list_display = ('parent', 'relationship_to_student')

@admin.register(AdminProfile)
class AdminProfileAdmin(admin.ModelAdmin):
    list_display = ('admin', 'department', 'position')

@admin.register(LibrarianProfile)
class LibrarianProfileAdmin(admin.ModelAdmin):
    list_display = ('librarian', 'employee_id')

@admin.register(FinanceProfile)
class FinanceProfileAdmin(admin.ModelAdmin):
    list_display = ('finance_officer', 'employee_id')

@admin.register(TransportProfile)
class TransportProfileAdmin(admin.ModelAdmin):
    list_display = ('transport_manager', 'employee_id')

@admin.register(SystemAdminProfile)
class SystemAdminProfileAdmin(admin.ModelAdmin):
    list_display = ('system_admin', 'employee_id', 'access_level')
    list_filter = ('access_level',)
