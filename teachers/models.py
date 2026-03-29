from django.db import models
from django.contrib.auth.models import User

class Teacher(models.Model):
    ROLE_CHOICES = [
        ('Admin', 'Admin'),
        ('Teacher', 'Teacher'),
    ]
    
    STATUS_CHOICES = [
        ('Active', 'Active'),
        ('Inactive', 'Inactive'),
    ]
    
    # Link to Django's User model
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='teacher_profile')
    
    # Internal ID (auto-increment integer)
    teacher_id = models.AutoField(primary_key=True)
    
    # Profile fields
    email = models.EmailField(max_length=50, blank=True, null=True)
    first_name = models.CharField(max_length=50, blank=True, null=True)
    middle_name = models.CharField(max_length=50, blank=True, null=True)
    last_name = models.CharField(max_length=50, blank=True, null=True)
    contact_number = models.CharField(max_length=15, blank=True, null=True)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='Active')
    is_first_login = models.BooleanField(default=True)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True)
    
    def __str__(self):
        return f"{self.user.username} - {self.role}"
    
    class Meta:
        ordering = ['teacher_id']


class TeacherAssignment(models.Model):
    assignment_id = models.AutoField(primary_key=True)
    section = models.ForeignKey(
        'sections.Section',
        on_delete=models.CASCADE,
        related_name='teacher_assignments'
    )
    teacher = models.ForeignKey(
        'teachers.Teacher',
        on_delete=models.CASCADE,
        related_name='teaching_assignments'
    )
    subject = models.ForeignKey(
        'subjects.Subject',
        on_delete=models.CASCADE,
        related_name='teacher_assignments'
    )
    schedule = models.ForeignKey(
        'schedules.ClassSchedule',
        on_delete=models.CASCADE,
        related_name='teacher_assignments'
    )
    school_year = models.ForeignKey(
        'school_years.SchoolYear',
        on_delete=models.CASCADE,
        related_name='teacher_assignments'
    )

    def __str__(self):
        return f"{self.teacher.user.username} - {self.subject.subject_code} ({self.section.section_code})"

    class Meta:
        ordering = ['school_year', 'section', 'subject']
