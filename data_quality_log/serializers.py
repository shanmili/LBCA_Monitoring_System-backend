from rest_framework import serializers
from .models import DataQualityLog


class DataQualityLogSerializer(serializers.ModelSerializer):
    student_id = serializers.PrimaryKeyRelatedField(source='student', queryset=DataQualityLog._meta.get_field('student').remote_field.model.objects.all())
    teacher_id = serializers.PrimaryKeyRelatedField(source='teacher', queryset=DataQualityLog._meta.get_field('teacher').remote_field.model.objects.all(), allow_null=True, required=False)
    student_pace_id = serializers.PrimaryKeyRelatedField(source='student_pace', queryset=DataQualityLog._meta.get_field('student_pace').remote_field.model.objects.all(), allow_null=True, required=False)

    class Meta:
        model = DataQualityLog
        fields = [
            'log_id',
            'student_id',
            'teacher_id',
            'student_pace_id',
            'issue_type',
            'resolved',
            'resolved_date',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['log_id', 'created_at', 'updated_at']
