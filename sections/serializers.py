from rest_framework import serializers
from .models import Section
from grade_levels.models import GradeLevel


class SectionSerializer(serializers.ModelSerializer):
    grade_level_display = serializers.CharField(source='grade_level.level', read_only=True)

    class Meta:
        model = Section
        fields = ['section_id', 'grade_level', 'grade_level_display', 'section_code', 'name']
        read_only_fields = ['section_id']

    def validate_grade_level(self, value):
        if not GradeLevel.objects.filter(grade_level_id=value.grade_level_id).exists():
            raise serializers.ValidationError("Grade level does not exist.")
        return value
