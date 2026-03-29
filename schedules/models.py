from django.db import models


class ClassSchedule(models.Model):
    DAY_CHOICES = [
        ('Monday', 'Monday'),
        ('Tuesday', 'Tuesday'),
        ('Wednesday', 'Wednesday'),
        ('Thursday', 'Thursday'),
        ('Friday', 'Friday'),
        ('Saturday', 'Saturday'),
    ]

    schedule_id = models.AutoField(primary_key=True)
    section = models.ForeignKey(
        'sections.Section',
        on_delete=models.CASCADE,
        related_name='class_schedules'
    )
    day = models.CharField(max_length=20, choices=DAY_CHOICES, unique=True)
    start_time = models.TimeField()
    end_time = models.TimeField()
    room = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.section.section_code} - {self.day} {self.start_time}-{self.end_time}"

    class Meta:
        ordering = ['section', 'day', 'start_time']
