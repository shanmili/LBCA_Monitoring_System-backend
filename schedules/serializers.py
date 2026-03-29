from rest_framework import serializers
from .models import ClassSchedule


class ClassScheduleSerializer(serializers.ModelSerializer):
    section_code = serializers.CharField(source='section.section_code', read_only=True)

    class Meta:
        model = ClassSchedule
        fields = ['schedule_id', 'section', 'section_code', 'day', 'start_time', 'end_time', 'room']
        read_only_fields = ['schedule_id']

    def validate(self, attrs):
        start_time = attrs.get('start_time')
        end_time = attrs.get('end_time')

        if start_time and end_time and start_time >= end_time:
            raise serializers.ValidationError({'end_time': 'End time must be later than start time.'})

        return attrs
