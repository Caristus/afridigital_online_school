import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from users.models import User, LibrarianProfile, FinanceProfile, TransportProfile
from django.db import IntegrityError

print("🔐 Creating/updating demo user accounts...")

# Demo accounts with passwords
demo_users = [
    {
        'email': 'admin@afridigital.com',
        'username': 'admin',
        'first_name': 'System',
        'last_name': 'Administrator',
        'role': 'admin',
        'password': 'admin123',
        'is_staff': True,
        'is_superuser': True
    },
    {
        'email': 'john.smith@afridigital.com',
        'username': 'john_smith',
        'first_name': 'John',
        'last_name': 'Smith',
        'role': 'teacher',
        'password': 'teacher123'
    },
    {
        'email': 'sarah.jones@afridigital.com',
        'username': 'sarah_jones',
        'first_name': 'Sarah',
        'last_name': 'Jones',
        'role': 'teacher',
        'password': 'teacher123'
    },
    {
        'email': 'student1@student.com',
        'username': 'student1',
        'first_name': 'Alice',
        'last_name': 'Johnson',
        'role': 'student',
        'password': 'student123'
    },
    {
        'email': 'student2@student.com',
        'username': 'student2',
        'first_name': 'Bob',
        'last_name': 'Williams',
        'role': 'student',
        'password': 'student123'
    },
    {
        'email': 'parent@parent.com',
        'username': 'parent',
        'first_name': 'Mary',
        'last_name': 'Johnson',
        'role': 'parent',
        'password': 'parent123'
    },
    {
        'email': 'librarian@afridigital.com',
        'username': 'librarian',
        'first_name': 'James',
        'last_name': 'Wilson',
        'role': 'librarian',
        'password': 'librarian123'
    },
    {
        'email': 'finance@afridigital.com',
        'username': 'finance',
        'first_name': 'Patricia',
        'last_name': 'Brown',
        'role': 'finance_officer',
        'password': 'finance123'
    },
    {
        'email': 'transport@afridigital.com',
        'username': 'transport',
        'first_name': 'Robert',
        'last_name': 'Davis',
        'role': 'transport_manager',
        'password': 'transport123'
    },
]

for data in demo_users:
    # Try to find user by email first
    try:
        user = User.objects.get(email=data['email'])
        # Update existing user
        user.username = data['username']
        user.first_name = data['first_name']
        user.last_name = data['last_name']
        user.role = data['role']
        user.is_staff = data.get('is_staff', False)
        user.is_superuser = data.get('is_superuser', False)
        user.set_password(data['password'])
        user.save()
        print(f"  🔄 Updated: {data['email']} ({data['role']})")
    except User.DoesNotExist:
        # User doesn't exist, try to create
        # But first check if username is taken
        username = data['username']
        original_username = username
        counter = 1
        
        while User.objects.filter(username=username).exists():
            username = f"{original_username}_{counter}"
            counter += 1
        
        try:
            user = User.objects.create_user(
                username=username,
                email=data['email'],
                password=data['password'],
                first_name=data['first_name'],
                last_name=data['last_name'],
                role=data['role'],
                is_staff=data.get('is_staff', False),
                is_superuser=data.get('is_superuser', False)
            )
            print(f"  ✅ Created: {data['email']} ({data['role']})")
        except IntegrityError as e:
            print(f"  ⚠️  Skipped {data['email']}: {e}")
            continue
    
    # Create profile for special roles
    if data['role'] == 'librarian':
        LibrarianProfile.objects.get_or_create(
            librarian=user,
            defaults={'employee_id': 'LIB001', 'department': 'Library'}
        )
    elif data['role'] == 'finance_officer':
        FinanceProfile.objects.get_or_create(
            finance_officer=user,
            defaults={'employee_id': 'FIN001', 'department': 'Finance'}
        )
    elif data['role'] == 'transport_manager':
        TransportProfile.objects.get_or_create(
            transport_manager=user,
            defaults={'employee_id': 'TRN001', 'department': 'Transport'}
        )

print("\n✅ All demo accounts created successfully!")
print("\n🔐 Login Credentials:")
print("  Admin:     admin@afridigital.com / admin123")
print("  Teacher:   john.smith@afridigital.com / teacher123")
print("  Student:   student1@student.com / student123")
print("  Parent:    parent@parent.com / parent123")
print("  Librarian: librarian@afridigital.com / librarian123")
print("  Finance:   finance@afridigital.com / finance123")
print("  Transport: transport@afridigital.com / transport123")
