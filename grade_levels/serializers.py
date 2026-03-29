from rest_framework import serializers
from .models import GradeLevel


class GradeLevelSerializer(serializers.ModelSerializer):
    class Meta:
        model = GradeLevel
        fields = ['grade_level_id', 'level', 'name']
        read_only_fields = ['grade_level_id']
