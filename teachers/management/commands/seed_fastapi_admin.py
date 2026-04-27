from django.contrib.auth.models import User
from django.core.management.base import BaseCommand
from django.db import transaction

from teachers.models import Teacher


class Command(BaseCommand):
    help = "Seed FastAPI-equivalent default admin account into Django."

    @transaction.atomic
    def handle(self, *args, **options):
        # FastAPI seed values (from seed_admin.py)
        admin_email = "admin@lbca.edu.ph"
        admin_password = "Admin123!"
        username_default = "ADMIN001"

        teacher = Teacher.objects.filter(email=admin_email).select_related('user').first()

        if teacher:
            user = teacher.user
            user.set_password(admin_password)
            user.email = admin_email
            if not user.username:
                user.username = username_default
            user.save()

            teacher.first_name = "System"
            teacher.last_name = "Administrator"
            teacher.middle_name = teacher.middle_name or ""
            teacher.contact_number = "+639123456789"
            teacher.role = "Admin"
            teacher.status = "Active"
            teacher.is_first_login = False
            teacher.save()

            self.stdout.write(self.style.SUCCESS("Admin already existed, password refreshed (FastAPI seed parity)."))
            self.stdout.write(
                f"Username: {user.username} | Email: {teacher.email} | Password: {admin_password}"
            )
            return

        user = User.objects.filter(username=username_default).first()
        if user is None:
            user = User.objects.create_user(
                username=username_default,
                email=admin_email,
                password=admin_password,
            )
        else:
            user.email = admin_email
            user.set_password(admin_password)
            user.save()

        teacher, created = Teacher.objects.get_or_create(
            user=user,
            defaults={
                'email': admin_email,
                'first_name': 'System',
                'middle_name': '',
                'last_name': 'Administrator',
                'contact_number': '+639123456789',
                'role': 'Admin',
                'status': 'Active',
                'is_first_login': False,
            },
        )

        if not created:
            teacher.email = admin_email
            teacher.first_name = 'System'
            teacher.middle_name = teacher.middle_name or ''
            teacher.last_name = 'Administrator'
            teacher.contact_number = '+639123456789'
            teacher.role = 'Admin'
            teacher.status = 'Active'
            teacher.is_first_login = False
            teacher.save()

        self.stdout.write(self.style.SUCCESS("FastAPI admin seed applied successfully."))
        self.stdout.write(
            f"Username: {user.username} | Email: {teacher.email} | Password: {admin_password}"
        )
