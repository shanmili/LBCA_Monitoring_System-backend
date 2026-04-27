"""
Django seeder: create or update a superuser with email username admin@lbca.edu.ph
Run inside the project's venv:
    .\venv\Scripts\python django_seed_admin.py
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lbca_backend.settings')
django.setup()

from django.contrib.auth import get_user_model
from teachers.models import Teacher

User = get_user_model()

EMAIL = "admin@lbca.edu.ph"
PASSWORD = "Admin123!"
ADMIN_EMAIL = "admin@lbca.edu.ph"
ADMIN_PASSWORD = "Admin123!"
TEACHER_EMAIL = "teacher@lbca.edu.ph"
TEACHER_PASSWORD = "Teacher123!"


def ensure_user(email, password, is_staff=False, is_superuser=False):
    user, created = User.objects.get_or_create(username=email, defaults={
        'email': email,
        'is_staff': is_staff,
        'is_superuser': is_superuser,
    })

    if not created:
        user.email = email
        user.is_staff = is_staff
        user.is_superuser = is_superuser

    user.set_password(password)
    user.save()
    return user, created


# Create/update admin
admin_user, admin_created = ensure_user(ADMIN_EMAIL, ADMIN_PASSWORD, is_staff=True, is_superuser=True)
admin_teacher, admin_teacher_created = Teacher.objects.get_or_create(user=admin_user, defaults={
    'email': ADMIN_EMAIL,
    'first_name': 'System',
    'last_name': 'Administrator',
    'contact_number': '+639123456789',
    'role': 'Admin',
    'status': 'Active',
    'is_first_login': False,
})

print(f"Admin user {'created' if admin_created else 'updated'}: {ADMIN_EMAIL}")
print(f"Admin Teacher profile {'created' if admin_teacher_created else 'exists'}.")

# Create/update teacher
teacher_user, teacher_created = ensure_user(TEACHER_EMAIL, TEACHER_PASSWORD, is_staff=False, is_superuser=False)
teacher_profile, teacher_profile_created = Teacher.objects.get_or_create(user=teacher_user, defaults={
    'email': TEACHER_EMAIL,
    'first_name': 'Teacher',
    'last_name': 'User',
    'contact_number': '+639111111111',
    'role': 'Teacher',
    'status': 'Active',
    'is_first_login': False,
})

print(f"Teacher user {'created' if teacher_created else 'updated'}: {TEACHER_EMAIL}")
print(f"Teacher profile {'created' if teacher_profile_created else 'exists'}.")
