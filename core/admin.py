from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import (
    User, Teacher, Section, Subject, Student, Guardian,
    Attendance, PaceRecord, Grade, RiskAssessment,
    Notification, ActivityLog, SchoolYear,
    TeacherSubjectAssignment, TeacherAvailability
)


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display    = ('username', 'role', 'email', 'is_active')
    list_filter     = ('role', 'is_active')
    search_fields   = ('username', 'email')
    ordering        = ('username',)
    fieldsets       = (
        (None, {'fields': ('username', 'password')}),
        ('Info', {'fields': ('email', 'role')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser')}),
    )
    add_fieldsets = (
        (None, {'fields': ('username', 'email', 'role', 'password1', 'password2')}),
    )


@admin.register(SchoolYear)
class SchoolYearAdmin(admin.ModelAdmin):
    list_display = ('year_label', 'is_current')


@admin.register(Teacher)
class TeacherAdmin(admin.ModelAdmin):
    list_display    = ('employee_id', 'last_name', 'first_name', 'email', 'is_active')
    list_filter     = ('is_active',)
    search_fields   = ('last_name', 'first_name', 'employee_id')


@admin.register(Section)
class SectionAdmin(admin.ModelAdmin):
    list_display = ('name', 'grade_level', 'adviser', 'school_year')
    list_filter  = ('grade_level', 'school_year')


@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display = ('name', 'color_hex')


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display    = ('student_id', 'last_name', 'first_name', 'section', 'school_year')
    list_filter     = ('section__grade_level', 'school_year')
    search_fields   = ('student_id', 'last_name', 'first_name')


@admin.register(Guardian)
class GuardianAdmin(admin.ModelAdmin):
    list_display = ('student', 'last_name', 'first_name', 'relationship', 'contact_number')


@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    list_display    = ('student', 'date', 'status')
    list_filter     = ('status', 'date')
    search_fields   = ('student__student_id', 'student__last_name')


@admin.register(PaceRecord)
class PaceRecordAdmin(admin.ModelAdmin):
    list_display    = ('student', 'subject', 'quarter', 'pace_number', 'completed', 'test_score')
    list_filter     = ('quarter', 'completed', 'subject')
    search_fields   = ('student__student_id',)


@admin.register(Grade)
class GradeAdmin(admin.ModelAdmin):
    list_display    = ('student', 'subject', 'quarter', 'grade_value', 'school_year')
    list_filter     = ('quarter', 'subject', 'school_year')


@admin.register(RiskAssessment)
class RiskAssessmentAdmin(admin.ModelAdmin):
    list_display    = ('student', 'risk_level', 'status', 'pace_percent', 'attendance_percent', 'is_latest')
    list_filter     = ('risk_level', 'status', 'is_latest')
    search_fields   = ('student__student_id', 'student__last_name')


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display    = ('recipient', 'notification_type', 'title', 'is_read', 'created_at')
    list_filter     = ('notification_type', 'is_read')


@admin.register(ActivityLog)
class ActivityLogAdmin(admin.ModelAdmin):
    list_display    = ('log_type', 'text', 'created_at')
    list_filter     = ('log_type',)


admin.site.register(TeacherSubjectAssignment)
admin.site.register(TeacherAvailability)
