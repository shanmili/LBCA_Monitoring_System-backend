from django.contrib import admin
from .models import Teacher, TeacherAssignment, TeacherAvailability

admin.site.register(Teacher)
admin.site.register(TeacherAssignment)
admin.site.register(TeacherAvailability)