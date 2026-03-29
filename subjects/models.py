from django.db import models


class Subject(models.Model):
    subject_id = models.AutoField(primary_key=True)
    grade_level = models.ForeignKey(
        'grade_levels.GradeLevel',
        on_delete=models.CASCADE,
        related_name='subjects'
    )
    subject_code = models.CharField(max_length=20, unique=True)
    subject_name = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.subject_code} - {self.subject_name}"

    class Meta:
        ordering = ['grade_level', 'subject_code']
