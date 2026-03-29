from rest_framework import serializers
from .models import Subject


class SubjectSerializer(serializers.ModelSerializer):
    grade_level_display = serializers.CharField(source='grade_level.level', read_only=True)

    class Meta:
        model = Subject
        fields = ['subject_id', 'grade_level', 'grade_level_display', 'subject_code', 'subject_name']
        read_only_fields = ['subject_id']
