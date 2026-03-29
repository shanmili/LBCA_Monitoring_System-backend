from django.db import models


class GradeLevel(models.Model):
    grade_level_id = models.AutoField(primary_key=True)
    level = models.CharField(max_length=10, unique=True)   # e.g. "Grade 1", "Grade 7"
    name = models.CharField(max_length=20)                  # e.g. "First Grade"

    def __str__(self):
        return f"{self.level} - {self.name}"

    class Meta:
        ordering = ['grade_level_id']
