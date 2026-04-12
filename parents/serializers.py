from rest_framework import serializers
from .models import Parent


class ParentSerializer(serializers.ModelSerializer):
    student_id = serializers.IntegerField(source='student.id', read_only=True)
    student_name = serializers.SerializerMethodField()

    class Meta:
        model = Parent
        fields = [
            'id', 'student', 'student_id', 'student_name',
            'first_name', 'middle_name', 'last_name',
            'email', 'phone', 'relationship', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']

    def get_student_name(self, obj):
        return f"{obj.student.first_name} {obj.student.last_name}"
