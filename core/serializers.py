from rest_framework import serializers
from django.contrib.auth import authenticate
from .models import (
    User, Teacher, Section, Subject, Student, Guardian,
    Attendance, PaceRecord, Grade, RiskAssessment,
    Notification, ActivityLog, SchoolYear,
    TeacherSubjectAssignment, TeacherAvailability
)


# ─── Auth Serializers ─────────────────────────────────────────────────────────
class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        user = authenticate(username=data['username'], password=data['password'])
        if not user:
            raise serializers.ValidationError('Invalid credentials.')
        if not user.is_active:
            raise serializers.ValidationError('Account is disabled.')
        data['user'] = user
        return data


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=6)

    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'role']

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'role', 'is_active']


# ─── School Year ──────────────────────────────────────────────────────────────
class SchoolYearSerializer(serializers.ModelSerializer):
    class Meta:
        model = SchoolYear
        fields = '__all__'


# ─── Subject ─────────────────────────────────────────────────────────────────
class SubjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subject
        fields = '__all__'


# ─── Teacher Availability ─────────────────────────────────────────────────────
class TeacherAvailabilitySerializer(serializers.ModelSerializer):
    class Meta:
        model = TeacherAvailability
        fields = ['day', 'is_available']


# ─── Teacher Subject Assignment ───────────────────────────────────────────────
class TeacherSubjectAssignmentSerializer(serializers.ModelSerializer):
    subject_name    = serializers.CharField(source='subject.name', read_only=True)
    section_name    = serializers.SerializerMethodField()
    availability    = TeacherAvailabilitySerializer(source='teacheravailability_set', many=True, read_only=True)

    class Meta:
        model = TeacherSubjectAssignment
        fields = ['id', 'subject', 'subject_name', 'section', 'section_name',
                  'consult_hours', 'availability']

    def get_section_name(self, obj):
        return str(obj.section)


# ─── Teacher ─────────────────────────────────────────────────────────────────
class TeacherSerializer(serializers.ModelSerializer):
    assignments = TeacherSubjectAssignmentSerializer(
        source='teachersubjectassignment_set', many=True, read_only=True
    )

    class Meta:
        model = Teacher
        fields = ['id', 'first_name', 'last_name', 'middle_name',
                  'email', 'employee_id', 'is_active', 'assignments']


# ─── Section ─────────────────────────────────────────────────────────────────
class SectionSerializer(serializers.ModelSerializer):
    adviser_name    = serializers.SerializerMethodField()
    school_year_label = serializers.CharField(source='school_year.year_label', read_only=True)

    class Meta:
        model = Section
        fields = ['id', 'name', 'grade_level', 'adviser', 'adviser_name', 'school_year_label']

    def get_adviser_name(self, obj):
        if obj.adviser:
            return f'{obj.adviser.last_name}, {obj.adviser.first_name}'
        return None


# ─── Guardian ────────────────────────────────────────────────────────────────
class GuardianSerializer(serializers.ModelSerializer):
    class Meta:
        model = Guardian
        fields = ['first_name', 'last_name', 'middle_name', 'contact_number', 'relationship']


# ─── Student ─────────────────────────────────────────────────────────────────
class StudentListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for list views."""
    section_name    = serializers.SerializerMethodField()
    grade_level     = serializers.CharField(source='section.grade_level', read_only=True)
    guardian        = GuardianSerializer(read_only=True)

    class Meta:
        model = Student
        fields = ['id', 'student_id', 'first_name', 'last_name', 'middle_name',
                  'gender', 'grade_level', 'section_name', 'guardian']

    def get_section_name(self, obj):
        return obj.section.name if obj.section else None


class StudentDetailSerializer(serializers.ModelSerializer):
    """Full serializer including risk, grades, attendance summary."""
    section_name        = serializers.SerializerMethodField()
    grade_level         = serializers.CharField(source='section.grade_level', read_only=True)
    guardian            = GuardianSerializer(read_only=True)
    latest_risk         = serializers.SerializerMethodField()
    attendance_summary  = serializers.SerializerMethodField()

    class Meta:
        model = Student
        fields = [
            'id', 'student_id', 'first_name', 'last_name', 'middle_name',
            'date_of_birth', 'gender', 'address', 'grade_level', 'section_name',
            'guardian', 'latest_risk', 'attendance_summary'
        ]

    def get_section_name(self, obj):
        return obj.section.name if obj.section else None

    def get_latest_risk(self, obj):
        risk = obj.risk_assessments.filter(is_latest=True).first()
        if risk:
            return RiskAssessmentSerializer(risk).data
        return None

    def get_attendance_summary(self, obj):
        records = obj.attendance_records.all()
        return {
            'present': records.filter(status='present').count(),
            'late': records.filter(status='late').count(),
            'absent': records.filter(status='absent').count(),
        }


# ─── Attendance ───────────────────────────────────────────────────────────────
class AttendanceSerializer(serializers.ModelSerializer):
    student_id = serializers.CharField(source='student.student_id', read_only=True)

    class Meta:
        model = Attendance
        fields = ['id', 'student', 'student_id', 'date', 'status', 'recorded_by']


# ─── PACE Record ──────────────────────────────────────────────────────────────
class PaceRecordSerializer(serializers.ModelSerializer):
    subject_name = serializers.CharField(source='subject.name', read_only=True)
    student_id   = serializers.CharField(source='student.student_id', read_only=True)

    class Meta:
        model = PaceRecord
        fields = [
            'id', 'student', 'student_id', 'subject', 'subject_name',
            'quarter', 'pace_number', 'completed', 'test_score',
            'recorded_by', 'updated_at'
        ]


# ─── Grade ───────────────────────────────────────────────────────────────────
class GradeSerializer(serializers.ModelSerializer):
    subject_name = serializers.CharField(source='subject.name', read_only=True)
    student_id   = serializers.CharField(source='student.student_id', read_only=True)

    class Meta:
        model = Grade
        fields = [
            'id', 'student', 'student_id', 'subject', 'subject_name',
            'quarter', 'grade_value', 'school_year', 'recorded_by', 'updated_at'
        ]


# ─── Risk Assessment ──────────────────────────────────────────────────────────
class RiskAssessmentSerializer(serializers.ModelSerializer):
    student_id   = serializers.CharField(source='student.student_id', read_only=True)
    student_name = serializers.SerializerMethodField()
    section      = serializers.SerializerMethodField()
    grade_level  = serializers.SerializerMethodField()

    class Meta:
        model = RiskAssessment
        fields = [
            'id', 'student', 'student_id', 'student_name', 'section', 'grade_level',
            'assessed_at', 'risk_level', 'status', 'pace_percent',
            'attendance_percent', 'trend', 'primary_factor',
            'secondary_factor', 'suggested_action', 'paces_behind', 'is_latest'
        ]

    def get_student_name(self, obj):
        s = obj.student
        return f'{s.last_name}, {s.first_name}'

    def get_section(self, obj):
        return obj.student.section.name if obj.student.section else None

    def get_grade_level(self, obj):
        return obj.student.section.grade_level if obj.student.section else None


# ─── Notification ─────────────────────────────────────────────────────────────
class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = ['id', 'notification_type', 'title', 'body', 'is_read', 'route', 'created_at']


# ─── Activity Log ─────────────────────────────────────────────────────────────
class ActivityLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = ActivityLog
        fields = ['id', 'log_type', 'text', 'created_at']


# ─── Dashboard Stats ──────────────────────────────────────────────────────────
class DashboardStatsSerializer(serializers.Serializer):
    total_students          = serializers.IntegerField()
    at_risk_count           = serializers.IntegerField()
    behind_pace_count       = serializers.IntegerField()
    avg_attendance_percent  = serializers.FloatField()
    avg_pace_percent        = serializers.FloatField()
