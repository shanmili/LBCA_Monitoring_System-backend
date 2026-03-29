from django.db import models


class SchoolYear(models.Model):
    school_year_id = models.AutoField(primary_key=True)
    year = models.CharField(max_length=20, unique=True)  # e.g. "2024-2025"
    is_current = models.BooleanField(default=False)
    start_date = models.DateField()
    end_date = models.DateField()

    def __str__(self):
        return self.year

    class Meta:
        ordering = ['-school_year_id']
