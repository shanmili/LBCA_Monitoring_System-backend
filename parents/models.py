from django.db import models
from students.models import Student


class Parent(models.Model):
    RELATIONSHIP_CHOICES = [
        ('Parent', 'Parent'),
        ('Guardian', 'Guardian'),
        ('Other', 'Other'),
    ]

    student = models.OneToOneField(Student, on_delete=models.CASCADE, related_name='parent_profile')
    first_name = models.CharField(max_length=50)
    middle_name = models.CharField(max_length=50, null=True, blank=True)
    last_name = models.CharField(max_length=50)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=15)
    relationship = models.CharField(max_length=10, choices=RELATIONSHIP_CHOICES, default='Parent')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'parents'

    def __str__(self):
        return f"{self.last_name}, {self.first_name} ({self.student})"
