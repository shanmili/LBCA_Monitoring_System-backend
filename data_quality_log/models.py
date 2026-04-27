from django.db import models


class DataQualityLog(models.Model):
	log_id = models.AutoField(primary_key=True)
	student = models.ForeignKey(
		'students.Student',
		on_delete=models.CASCADE,
		related_name='quality_logs'
	)
	teacher = models.ForeignKey(
		'teachers.Teacher',
		on_delete=models.SET_NULL,
		null=True,
		blank=True,
		related_name='quality_logs'
	)
	student_pace = models.ForeignKey(
		'student_pace.StudentPace',
		on_delete=models.SET_NULL,
		null=True,
		blank=True,
		related_name='quality_logs'
	)
	issue_type = models.CharField(max_length=100)
	resolved = models.BooleanField(default=False)
	resolved_date = models.DateTimeField(null=True, blank=True)
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)

	class Meta:
		db_table = 'data_quality_logs'
		ordering = ['-created_at']

	def __str__(self):
		return f"{self.student} - {self.issue_type}"
