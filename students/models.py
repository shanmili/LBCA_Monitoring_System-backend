from django.db import models
from django.contrib.auth.models import User


class Student(models.Model):
    GENDER_CHOICES = [
        ('Male', 'Male'),
        ('Female', 'Female'),
    ]
    RELATIONSHIP_CHOICES = [
        ('Parent', 'Parent'),
        ('Guardian', 'Guardian'),
        ('Other', 'Other'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='student_profile')
    first_name = models.CharField(max_length=50)
    middle_name = models.CharField(max_length=50, null=True, blank=True)
    last_name = models.CharField(max_length=50)
    birth_date = models.CharField(max_length=15)
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES)
    address = models.CharField(max_length=255)
    guardian_first_name = models.CharField(max_length=50)
    guardian_mid_name = models.CharField(max_length=50, null=True, blank=True)
    guardian_last_name = models.CharField(max_length=50)
    guardian_contact = models.CharField(max_length=15)
    relationship = models.CharField(max_length=10, choices=RELATIONSHIP_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_students'
    )

    class Meta:
        db_table = 'students'

    def __str__(self):
        return f"{self.last_name}, {self.first_name}"


class StudentEnrollment(models.Model):
    END_OF_YEAR_CHOICES = [
        ('Promoted', 'Promoted'),
        ('Retained', 'Retained'),
        ('Dropped', 'Dropped'),
        ('Graduated', 'Graduated'),
    ]

    student = models.ForeignKey(
        'students.Student',
        on_delete=models.CASCADE,
        related_name='enrollments'
    )
    grade_level = models.ForeignKey(
        'grade_levels.GradeLevel',
        on_delete=models.PROTECT
    )
    section = models.ForeignKey(
        'sections.Section',
        on_delete=models.PROTECT
    )
    enrolled_by = models.ForeignKey(
        'teachers.Teacher',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='enrolled_students'
    )
    next_grade_level = models.ForeignKey(
        'grade_levels.GradeLevel',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='next_grade_enrollments'
    )
    school_year = models.ForeignKey(
        'school_years.SchoolYear',
        on_delete=models.PROTECT
    )
    enrollment_date = models.DateField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    end_of_year_status = models.CharField(
        max_length=20,
        choices=END_OF_YEAR_CHOICES,
        null=True,
        blank=True
    )

    class Meta:
        db_table = 'student_enrollments'

    def __str__(self):
        return f"{self.student} - {self.school_year}"