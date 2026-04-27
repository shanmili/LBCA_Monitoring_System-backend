from rest_framework import serializers
from .models import Subject


class SubjectSerializer(serializers.ModelSerializer):
    grade_level_id = serializers.PrimaryKeyRelatedField(source='grade_level', queryset=Subject._meta.get_field('grade_level').remote_field.model.objects.all())

    class Meta:
        model = Subject
        fields = ['subject_id', 'grade_level_id', 'subject_name', 'subject_code', 'is_active']
        read_only_fields = ['subject_id']
