from rest_framework import serializers
from .models import StudentPace, EarlyWarning


class StudentPaceSerializer(serializers.ModelSerializer):
    pace_id = serializers.IntegerField(source='id', read_only=True)
    student_id = serializers.PrimaryKeyRelatedField(source='student', queryset=StudentPace._meta.get_field('student').remote_field.model.objects.all())
    enrollment_id = serializers.PrimaryKeyRelatedField(source='enrollment', queryset=StudentPace._meta.get_field('enrollment').remote_field.model.objects.all())
    student_name = serializers.SerializerMethodField()
    
    class Meta:
        model = StudentPace
        fields = [
            'pace_id', 'student_id', 'student_name', 'enrollment_id',
            'subject', 'pace_percent', 'paces_behind',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']

    def get_student_name(self, obj):
        return f"{obj.student.first_name} {obj.student.last_name}"


class EarlyWarningSerializer(serializers.ModelSerializer):
    warning_id = serializers.IntegerField(source='id', read_only=True)
    student_id = serializers.PrimaryKeyRelatedField(source='student', queryset=EarlyWarning._meta.get_field('student').remote_field.model.objects.all())
    enrollment_id = serializers.PrimaryKeyRelatedField(source='enrollment', queryset=EarlyWarning._meta.get_field('enrollment').remote_field.model.objects.all(), allow_null=True, required=False)
    student_name = serializers.SerializerMethodField()
    
    class Meta:
        model = EarlyWarning
        fields = [
            'warning_id', 'student_id', 'student_name', 'enrollment_id',
            'subject', 'teacher', 'risk_level',
            'paces_behind', 'pace_percent', 'attendance',
            'status', 'trend', 'last_activity',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']

    def get_student_name(self, obj):
        return f"{obj.student.first_name} {obj.student.last_name}"
