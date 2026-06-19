import os
import django
from datetime import date, timedelta
from decimal import Decimal

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from users.models import User, StudentProfile, TeacherProfile, ParentProfile
from core.models import AcademicYear, Term
from academics.models import Subject, Class, Course, Module, Lesson, Enrollment
from assessments.models import Assessment, Question, Answer, Submission, Grade
from finance.models import FeeStructure, Invoice, Payment
from attendance.models import AttendanceSession, AttendanceRecord
from timetable.models import Room, Timetable, ClassSession
from library.models import Book, BorrowRecord
from transport.models import Bus, Route, StudentTransportAllocation

print("🎓 Creating sample data for AfriDigital School...")

# Create Academic Year and Term
print("📅 Creating academic year and term...")
academic_year, _ = AcademicYear.objects.get_or_create(
    name="2025/2026",
    defaults={
        'start_date': date(2025, 9, 1),
        'end_date': date(2026, 7, 31),
        'is_current': True
    }
)

term1, _ = Term.objects.get_or_create(
    name="Term 1",
    academic_year=academic_year,
    defaults={
        'start_date': date(2025, 9, 1),
        'end_date': date(2025, 12, 20),
        'is_current': True
    }
)

# Create Admin User
print("👤 Creating admin user...")
admin_user, created = User.objects.get_or_create(
    email='admin@afridigital.com',
    defaults={
        'username': 'admin',
        'first_name': 'System',
        'last_name': 'Administrator',
        'role': 'admin',
        'is_staff': True,
        'is_superuser': True
    }
)
if created:
    admin_user.set_password('admin123')
    admin_user.save()

# Create Teachers
print("👨‍🏫 Creating teachers...")
teachers_data = [
    {'email': 'john.smith@afridigital.com', 'first_name': 'John', 'last_name': 'Smith', 'subject': 'Mathematics'},
    {'email': 'sarah.jones@afridigital.com', 'first_name': 'Sarah', 'last_name': 'Jones', 'subject': 'English'},
    {'email': 'michael.brown@afridigital.com', 'first_name': 'Michael', 'last_name': 'Brown', 'subject': 'Science'},
]

teachers = []
for data in teachers_data:
    teacher_user, created = User.objects.get_or_create(
        email=data['email'],
        defaults={
            'username': data['email'].split('@')[0],
            'first_name': data['first_name'],
            'last_name': data['last_name'],
            'role': 'teacher'
        }
    )
    if created:
        teacher_user.set_password('teacher123')
        teacher_user.save()
    
    teacher_profile, _ = TeacherProfile.objects.get_or_create(
        teacher=teacher_user,
        defaults={
            'employee_id': f"T{len(teachers)+1:04d}",
            'qualification': 'Bachelor of Education',
            'specialization': data['subject']
        }
    )
    teachers.append(teacher_profile)

# Create Students
print("👨‍🎓 Creating students...")
students_data = [
    {'email': 'student1@student.com', 'first_name': 'Alice', 'last_name': 'Johnson', 'admission': 'STD001'},
    {'email': 'student2@student.com', 'first_name': 'Bob', 'last_name': 'Williams', 'admission': 'STD002'},
    {'email': 'student3@student.com', 'first_name': 'Carol', 'last_name': 'Davis', 'admission': 'STD003'},
    {'email': 'student4@student.com', 'first_name': 'David', 'last_name': 'Miller', 'admission': 'STD004'},
    {'email': 'student5@student.com', 'first_name': 'Emma', 'last_name': 'Wilson', 'admission': 'STD005'},
]

students = []
for data in students_data:
    student_user, created = User.objects.get_or_create(
        email=data['email'],
        defaults={
            'username': data['email'].split('@')[0],
            'first_name': data['first_name'],
            'last_name': data['last_name'],
            'role': 'student'
        }
    )
    if created:
        student_user.set_password('student123')
        student_user.save()
    
    student_profile, _ = StudentProfile.objects.get_or_create(
        student=student_user,
        defaults={
            'admission_number': data['admission'],
            'date_of_birth': date(2008, 5, 15),
            'gender': 'F' if data['first_name'] in ['Alice', 'Carol', 'Emma'] else 'M'
        }
    )
    students.append(student_profile)

# Create Parent
print("👪 Creating parent...")
parent_user, created = User.objects.get_or_create(
    email='parent@parent.com',
    defaults={
        'username': 'parent',
        'first_name': 'Mary',
        'last_name': 'Johnson',
        'role': 'parent'
    }
)
if created:
    parent_user.set_password('parent123')
    parent_user.save()

parent_profile, _ = ParentProfile.objects.get_or_create(
    parent=parent_user,
    defaults={
        'occupation': 'Business Owner',
        'relationship_to_student': 'Mother'
    }
)

# Link parent to first student
students[0].parent = parent_user
students[0].save()

# Create Subjects
print("📚 Creating subjects...")
subjects_data = [
    {'name': 'Mathematics', 'code': 'MATH101'},
    {'name': 'English', 'code': 'ENG101'},
    {'name': 'Science', 'code': 'SCI101'},
    {'name': 'History', 'code': 'HIS101'},
]

subjects = []
for data in subjects_data:
    subject, _ = Subject.objects.get_or_create(
        code=data['code'],
        defaults={'name': data['name'], 'credit_hours': 3}
    )
    subjects.append(subject)

# Create Class
print("🏫 Creating class...")
grade10a, _ = Class.objects.get_or_create(
    name="Grade 10A",
    academic_year=academic_year,
    defaults={
        'grade_level': 10,
        'capacity': 30,
        'class_teacher': teachers[0]
    }
)

# Assign students to class
for student in students:
    student.current_class = grade10a
    student.save()

# Create Courses
print("📖 Creating courses...")
courses = []
for i, (subject, teacher) in enumerate(zip(subjects, teachers[:len(subjects)])):
    course, _ = Course.objects.get_or_create(
        code=f"{subject.code}_T1",
        defaults={
            'title': f"{subject.name} - Term 1",
            'description': f"Comprehensive {subject.name} course for Grade 10",
            'subject': subject,
            'teacher': teacher,
            'class_assigned': grade10a,
            'term': term1,
            'is_published': True
        }
    )
    courses.append(course)

# Create Modules and Lessons
print("📝 Creating modules and lessons...")
for course in courses:
    for module_num in range(1, 4):
        module, _ = Module.objects.get_or_create(
            course=course,
            title=f"Module {module_num}: {course.subject.name} Fundamentals",
            defaults={
                'description': f"Learn the basics of {course.subject.name}",
                'order': module_num,
                'is_published': True
            }
        )
        
        for lesson_num in range(1, 3):
            Lesson.objects.get_or_create(
                module=module,
                title=f"Lesson {lesson_num}: Introduction to {course.subject.name}",
                defaults={
                    'content': f"This lesson covers the fundamentals of {course.subject.name}.",
                    'order': lesson_num,
                    'duration_minutes': 45,
                    'is_published': True
                }
            )

# Enroll students in courses
print("🎯 Enrolling students...")
for student in students:
    for course in courses:
        Enrollment.objects.get_or_create(
            student=student,
            course=course,
            defaults={'is_active': True}
        )

# Create Assessments
print("📝 Creating assessments...")
for course in courses:
    assessment, _ = Assessment.objects.get_or_create(
        title=f"{course.subject.name} Mid-Term Exam",
        course=course,
        defaults={
            'description': f"Mid-term examination for {course.subject.name}",
            'assessment_type': 'exam',
            'total_marks': Decimal('100.00'),
            'passing_marks': Decimal('50.00'),
            'duration_minutes': 120,
            'start_date': date.today() - timedelta(days=10),
            'end_date': date.today() + timedelta(days=20),
            'is_published': True,
            'created_by': course.teacher,
            'term': term1
        }
    )
    
    # Add questions
    for q_num in range(1, 6):
        question, _ = Question.objects.get_or_create(
            assessment=assessment,
            question_text=f"Question {q_num}: What is the fundamental concept of {course.subject.name}?",
            defaults={
                'question_type': 'multiple_choice',
                'marks': Decimal('20.00'),
                'order': q_num
            }
        )
        
        # Add answers
        for a_num in range(1, 4):
            Answer.objects.get_or_create(
                question=question,
                answer_text=f"Answer option {a_num}",
                defaults={
                    'is_correct': (a_num == 1),
                    'order': a_num
                }
            )

# Create Fee Structure and Invoices
print("💰 Creating finance data...")
fee_structure, _ = FeeStructure.objects.get_or_create(
    name="Term 1 Tuition Fee",
    academic_year=academic_year,
    defaults={
        'amount': Decimal('50000.00'),
        'due_date': date.today() + timedelta(days=30),
        'is_active': True
    }
)

for student in students:
    invoice, _ = Invoice.objects.get_or_create(
        invoice_number=f"INV-{student.admission_number}-T1",
        defaults={
            'student': student,
            'fee_structure': fee_structure,
            'amount': fee_structure.amount,
            'due_date': fee_structure.due_date,
            'status': 'pending'
        }
    )
    
    # Create partial payment for first 2 students
    if students.index(student) < 2:
        payment, _ = Payment.objects.get_or_create(
            payment_reference=f"PAY-{student.admission_number}-001",
            defaults={
                'invoice': invoice,
                'amount': Decimal('25000.00'),
                'payment_method': 'mpesa',
                'transaction_id': f"MPESA{student.admission_number}001"
            }
        )

# Create Attendance Records
print("📅 Creating attendance records...")
for student in students:
    session, _ = AttendanceSession.objects.get_or_create(
        class_assigned=grade10a,
        date=date.today(),
        session_type='daily',
        defaults={
            'term': term1,
            'created_by': teachers[0]
        }
    )
    
    # Random attendance status
    import random
    status = random.choice(['present', 'present', 'present', 'late', 'absent'])
    AttendanceRecord.objects.get_or_create(
        session=session,
        student=student,
        defaults={'status': status}
    )

# Create Timetable
print("🗓️ Creating timetable...")
timetable, _ = Timetable.objects.get_or_create(
    name="Grade 10A - Term 1",
    class_assigned=grade10a,
    defaults={
        'term': term1,
        'academic_year': academic_year
    }
)

rooms_data = [
    {'name': 'Room 101', 'capacity': 30},
    {'name': 'Room 102', 'capacity': 30},
    {'name': 'Science Lab', 'capacity': 25},
]

rooms = []
for data in rooms_data:
    room, _ = Room.objects.get_or_create(
        name=data['name'],
        defaults={'capacity': data['capacity']}
    )
    rooms.append(room)

days = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday']
from datetime import time

for i, course in enumerate(courses):
    for day_idx in range(min(3, len(days))):
        ClassSession.objects.get_or_create(
            timetable=timetable,
            subject=course.subject,
            day=days[day_idx],
            start_time=time(8 + i, 0),
            defaults={
                'teacher': course.teacher,
                'room': rooms[i % len(rooms)],
                'end_time': time(9 + i, 0)
            }
        )

# Create Library Books
print("📚 Creating library books...")
books_data = [
    {'title': 'Introduction to Algebra', 'author': 'John Smith', 'isbn': '978-0-123456-47-2', 'category': 'Mathematics'},
    {'title': 'English Literature', 'author': 'Sarah Jones', 'isbn': '978-0-123456-48-9', 'category': 'English'},
    {'title': 'Basic Physics', 'author': 'Michael Brown', 'isbn': '978-0-123456-49-6', 'category': 'Science'},
    {'title': 'World History', 'author': 'David Wilson', 'isbn': '978-0-123456-50-2', 'category': 'History'},
    {'title': 'Advanced Mathematics', 'author': 'John Smith', 'isbn': '978-0-123456-51-9', 'category': 'Mathematics'},
]

for data in books_data:
    book, _ = Book.objects.get_or_create(
        isbn=data['isbn'],
        defaults={
            'title': data['title'],
            'author': data['author'],
            'category': data['category'],
            'total_copies': 5,
            'available_copies': 4
        }
    )

# Create Transport
print("🚌 Creating transport data...")
bus1, _ = Bus.objects.get_or_create(
    bus_number="BUS001",
    defaults={
        'capacity': 40,
        'driver_name': 'Peter Kamau',
        'driver_phone': '+254712345678'
    }
)

route1, _ = Route.objects.get_or_create(
    name="Route A - North",
    defaults={
        'distance_km': Decimal('15.5'),
        'monthly_fee': Decimal('3000.00'),
        'is_active': True
    }
)

# Assign first 3 students to transport
for student in students[:3]:
    StudentTransportAllocation.objects.get_or_create(
        student=student,
        academic_year=academic_year,
        defaults={
            'bus': bus1,
            'route': route1,
        }
    )

print("\n✅ Sample data created successfully!")
print("\n📊 Summary:")
print(f"  - Users: {User.objects.count()}")
print(f"  - Students: {StudentProfile.objects.count()}")
print(f"  - Teachers: {TeacherProfile.objects.count()}")
print(f"  - Courses: {Course.objects.count()}")
print(f"  - Assessments: {Assessment.objects.count()}")
print(f"  - Invoices: {Invoice.objects.count()}")
print(f"  - Books: {Book.objects.count()}")
print(f"  - Buses: {Bus.objects.count()}")

print("\n🔐 Login Credentials:")
print("  Admin: admin@afridigital.com / admin123")
print("  Teacher: john.smith@afridigital.com / teacher123")
print("  Student: student1@student.com / student123")
print("  Parent: parent@parent.com / parent123")
