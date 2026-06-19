import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from users.models import User, SystemAdminProfile

print("🔐 Creating System Administrator account...")

user, created = User.objects.get_or_create(
    email='sysadmin@afridigital.com',
    defaults={
        'username': 'sysadmin',
        'first_name': 'System',
        'last_name': 'Administrator',
        'role': 'system_admin',
        'is_staff': True,
        'is_superuser': True,
    }
)

if created:
    user.set_password('sysadmin123')
    user.save()
    print("  ✅ Created System Administrator account")
else:
    user.role = 'system_admin'
    user.is_staff = True
    user.is_superuser = True
    user.set_password('sysadmin123')
    user.save()
    print("  🔄 Updated System Administrator account")

SystemAdminProfile.objects.get_or_create(
    system_admin=user,
    defaults={
        'employee_id': 'SYS001',
        'access_level': 'full'
    }
)

print("\n✅ System Administrator account ready!")
print("\n🔐 Login Credentials:")
print("  System Admin: sysadmin@afridigital.com / sysadmin123")
print("  Access: Full system access including /django-admin/")
