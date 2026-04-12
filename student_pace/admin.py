from django.contrib import admin
from .models import StudentPace, EarlyWarning


@admin.register(StudentPace)
class StudentPaceAdmin(admin.ModelAdmin):
    list_display = ('id', 'student', 'enrollment', 'subject', 'pace_percent', 'paces_behind', 'updated_at')
    list_filter = ('subject', 'created_at', 'updated_at')
    search_fields = ('student__first_name', 'student__last_name', 'subject')
    readonly_fields = ('created_at', 'updated_at')
    ordering = ('-updated_at',)


@admin.register(EarlyWarning)
class EarlyWarningAdmin(admin.ModelAdmin):
    list_display = ('id', 'student', 'subject', 'teacher', 'risk_level', 'status', 'trend', 'updated_at')
    list_filter = ('risk_level', 'status', 'trend', 'created_at')
    search_fields = ('student__first_name', 'student__last_name', 'subject', 'teacher')
    readonly_fields = ('created_at', 'updated_at')
    ordering = ('-created_at',)

