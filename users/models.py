from django.contrib.auth.models import AbstractUser
from django.db import models
import uuid

class User(AbstractUser):
    ROLE_CHOICES = [
        ('system_admin', 'System Administrator'),
        ('admin', 'School Administrator'),
        ('teacher', 'Teacher'),
        ('student', 'Student'),
        ('parent', 'Parent'),
        ('librarian', 'Librarian'),
        ('finance_officer', 'Finance Officer'),
        ('transport_manager', 'Transport Manager'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='student')
    profile_picture = models.ImageField(upload_to='profile_pics/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']
    
    class Meta:
        verbose_name = "User"
        verbose_name_plural = "Users"
    
    def __str__(self):
        return f"{self.get_full_name()} ({self.email})"

class StudentProfile(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    student = models.OneToOneField(User, on_delete=models.CASCADE, related_name='student_profile')
    admission_number = models.CharField(max_length=50, unique=True)
    date_of_birth = models.DateField()
    gender = models.CharField(max_length=10, choices=[('M', 'Male'), ('F', 'Female'), ('O', 'Other')])
    current_class = models.ForeignKey('academics.Class', on_delete=models.SET_NULL, null=True, blank=True)
    parent = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='children')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Student Profile"
        verbose_name_plural = "Student Profiles"

    def __str__(self):
        return f"{self.student.get_full_name()} - {self.admission_number}"

class TeacherProfile(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    teacher = models.OneToOneField(User, on_delete=models.CASCADE, related_name='teacher_profile')
    employee_id = models.CharField(max_length=50, unique=True)
    qualification = models.CharField(max_length=200)
    specialization = models.CharField(max_length=200)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Teacher Profile"
        verbose_name_plural = "Teacher Profiles"

    def __str__(self):
        return f"{self.teacher.get_full_name()} - {self.employee_id}"

class ParentProfile(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    parent = models.OneToOneField(User, on_delete=models.CASCADE, related_name='parent_profile')
    occupation = models.CharField(max_length=200, blank=True, null=True)
    relationship_to_student = models.CharField(max_length=100, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Parent Profile"
        verbose_name_plural = "Parent Profiles"

    def __str__(self):
        return f"{self.parent.get_full_name()}"

class AdminProfile(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    admin = models.OneToOneField(User, on_delete=models.CASCADE, related_name='admin_profile')
    department = models.CharField(max_length=200)
    position = models.CharField(max_length=200)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Admin Profile"
        verbose_name_plural = "Admin Profiles"

    def __str__(self):
        return f"{self.admin.get_full_name()} - {self.position}"

class LibrarianProfile(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    librarian = models.OneToOneField(User, on_delete=models.CASCADE, related_name='librarian_profile')
    employee_id = models.CharField(max_length=50, unique=True)
    department = models.CharField(max_length=100, default='Library')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Librarian Profile"
        verbose_name_plural = "Librarian Profiles"

    def __str__(self):
        return f"{self.librarian.get_full_name()} - Librarian"

class FinanceProfile(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    finance_officer = models.OneToOneField(User, on_delete=models.CASCADE, related_name='finance_profile')
    employee_id = models.CharField(max_length=50, unique=True)
    department = models.CharField(max_length=100, default='Finance')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Finance Profile"
        verbose_name_plural = "Finance Profiles"

    def __str__(self):
        return f"{self.finance_officer.get_full_name()} - Finance"

class TransportProfile(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    transport_manager = models.OneToOneField(User, on_delete=models.CASCADE, related_name='transport_profile')
    employee_id = models.CharField(max_length=50, unique=True)
    department = models.CharField(max_length=100, default='Transport')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Transport Profile"
        verbose_name_plural = "Transport Profiles"

    def __str__(self):
        return f"{self.transport_manager.get_full_name()} - Transport"

class SystemAdminProfile(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    system_admin = models.OneToOneField(User, on_delete=models.CASCADE, related_name='system_admin_profile')
    employee_id = models.CharField(max_length=50, unique=True)
    access_level = models.CharField(max_length=50, choices=[
        ('full', 'Full Access'),
        ('technical', 'Technical Only'),
        ('monitoring', 'Monitoring Only'),
    ], default='full')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "System Admin Profile"
        verbose_name_plural = "System Admin Profiles"

    def __str__(self):
        return f"{self.system_admin.get_full_name()} - System Admin ({self.access_level})"
