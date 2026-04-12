from rest_framework import serializers
from .models import StudentPace, EarlyWarning


class StudentPaceSerializer(serializers.ModelSerializer):
    student_name = serializers.SerializerMethodField()
    
    class Meta:
        model = StudentPace
        fields = [
            'id', 'student', 'student_name', 'enrollment',
            'subject', 'pace_percent', 'paces_behind',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']

    def get_student_name(self, obj):
        return f"{obj.student.first_name} {obj.student.last_name}"


class EarlyWarningSerializer(serializers.ModelSerializer):
    student_name = serializers.SerializerMethodField()
    teacher_name = serializers.CharField(source='teacher', read_only=False)
    
    class Meta:
        model = EarlyWarning
        fields = [
            'id', 'student', 'student_name', 'enrollment',
            'subject', 'teacher', 'teacher_name', 'risk_level',
            'paces_behind', 'pace_percent', 'attendance',
            'status', 'trend', 'last_activity',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']

    def get_student_name(self, obj):
        return f"{obj.student.first_name} {obj.student.last_name}"
