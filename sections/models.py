from django.db import models
from grade_levels.models import GradeLevel


class Section(models.Model):
    section_id = models.AutoField(primary_key=True)
    grade_level = models.ForeignKey(
        GradeLevel,
        on_delete=models.CASCADE,
        related_name='sections'
    )
    section_code = models.CharField(max_length=20, unique=True)  # e.g. "7-A"
    name = models.CharField(max_length=30)                        # e.g. "Section A"

    def __str__(self):
        return f"{self.section_code} - {self.name}"

    class Meta:
        ordering = ['grade_level', 'section_id']
