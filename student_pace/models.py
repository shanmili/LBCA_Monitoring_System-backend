from django.db import models
from django.contrib.auth.models import User


class StudentPace(models.Model):
    """
    Tracks student pace and progress through curriculum
    """
    student = models.ForeignKey('students.Student', on_delete=models.CASCADE, related_name='paces')
    enrollment = models.ForeignKey('students.StudentEnrollment', on_delete=models.CASCADE, related_name='paces')
    subject = models.CharField(max_length=100)
    pace_percent = models.FloatField(default=0.0, help_text='Percentage of curriculum completed')
    paces_behind = models.IntegerField(default=0, help_text='Number of paces behind standard')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'student_paces'
        ordering = ['-updated_at']

    def __str__(self):
        return f"{self.student} - {self.subject} ({self.pace_percent}%)"


class EarlyWarning(models.Model):
    """
    Early warning system to flag students at risk
    """
    RISK_LEVEL_CHOICES = [
        ('critical', 'Critical'),
        ('high', 'High'),
        ('moderate', 'Moderate'),
        ('low', 'Low'),
    ]
    STATUS_CHOICES = [
        ('Critical', 'Critical'),
        ('At Risk', 'At Risk'),
        ('Warning', 'Warning'),
        ('On Track', 'On Track'),
    ]
    TREND_CHOICES = [
        ('declining', 'Declining'),
        ('stable', 'Stable'),
        ('improving', 'Improving'),
    ]

    student = models.ForeignKey('students.Student', on_delete=models.CASCADE, related_name='early_warnings')
    enrollment = models.ForeignKey('students.StudentEnrollment', on_delete=models.CASCADE, null=True, blank=True, related_name='early_warnings')
    subject = models.CharField(max_length=100)
    teacher = models.CharField(max_length=100)
    risk_level = models.CharField(max_length=20, choices=RISK_LEVEL_CHOICES)
    paces_behind = models.IntegerField(default=0)
    pace_percent = models.FloatField(default=0.0)
    attendance = models.FloatField(default=0.0, help_text='Attendance percentage')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES)
    trend = models.CharField(max_length=20, choices=TREND_CHOICES)
    last_activity = models.CharField(max_length=100, default="Today")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'early_warnings'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.student} - {self.subject} ({self.risk_level})"

