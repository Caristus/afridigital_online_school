from django.contrib import admin
from django.contrib.auth.models import User, Group
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from users.models import (
    User as CustomUser, 
    StudentProfile, 
    TeacherProfile, 
    ParentProfile,
    AdminProfile,
    LibrarianProfile,
    FinanceProfile,
    TransportProfile
)

# Unregister default User and Group
admin.site.unregister(User)
admin.site.unregister(Group)

@admin.register(CustomUser)
class CustomUserAdmin(BaseUserAdmin):
    list_display = ('email', 'username', 'role', 'first_name', 'last_name', 'is_staff', 'is_active')
    list_filter = ('role', 'is_staff', 'is_active', 'is_superuser')
    fieldsets = (
        (None, {'fields': ('email', 'username', 'password')}),
        ('Personal Info', {'fields': ('first_name', 'last_name', 'phone', 'profile_picture')}),
        ('Role & Permissions', {'fields': ('role', 'is_staff', 'is_active', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important Dates', {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'username', 'role', 'password1', 'password2', 'is_staff', 'is_active'),
        }),
    )
    search_fields = ('email', 'username', 'first_name', 'last_name')
    ordering = ('email',)

@admin.register(StudentProfile)
class StudentProfileAdmin(admin.ModelAdmin):
    list_display = ('student', 'admission_number', 'current_class', 'gender', 'enrollment_date')
    list_filter = ('gender', 'current_class')
    search_fields = ('admission_number', 'student__first_name', 'student__last_name', 'student__email')
    readonly_fields = ('enrollment_date',)

@admin.register(TeacherProfile)
class TeacherProfileAdmin(admin.ModelAdmin):
    list_display = ('teacher', 'employee_id', 'specialization', 'qualification', 'hire_date')
    list_filter = ('specialization',)
    search_fields = ('employee_id', 'teacher__first_name', 'teacher__last_name')
    readonly_fields = ('hire_date',)

@admin.register(ParentProfile)
class ParentProfileAdmin(admin.ModelAdmin):
    list_display = ('parent', 'occupation', 'relationship_to_student')
    search_fields = ('parent__first_name', 'parent__last_name', 'parent__email')

@admin.register(AdminProfile)
class AdminProfileAdmin(admin.ModelAdmin):
    list_display = ('admin', 'department', 'position')
    list_filter = ('department',)
    search_fields = ('admin__first_name', 'admin__last_name')

@admin.register(LibrarianProfile)
class LibrarianProfileAdmin(admin.ModelAdmin):
    list_display = ('librarian', 'employee_id', 'department')
    search_fields = ('employee_id', 'librarian__first_name', 'librarian__last_name')

@admin.register(FinanceProfile)
class FinanceProfileAdmin(admin.ModelAdmin):
    list_display = ('finance_officer', 'employee_id', 'department')
    search_fields = ('employee_id', 'finance_officer__first_name', 'finance_officer__last_name')

@admin.register(TransportProfile)
class TransportProfileAdmin(admin.ModelAdmin):
    list_display = ('transport_manager', 'employee_id', 'department')
    search_fields = ('employee_id', 'transport_manager__first_name', 'transport_manager__last_name')

# Admin Site Customization
admin.site.site_header = "🎓 AfriDigital School Administration"
admin.site.site_title = "AfriDigital Admin Portal"
admin.site.index_title = "Welcome to AfriDigital School Management System"
