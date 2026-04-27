from rest_framework import serializers
from .models import ClassSchedule
from sections.models import Section


class ClassScheduleSerializer(serializers.ModelSerializer):
    section_id = serializers.PrimaryKeyRelatedField(source='section', queryset=Section.objects.all())
    time_start = serializers.TimeField(source='start_time')
    time_end = serializers.TimeField(source='end_time')
    classroom = serializers.CharField(source='room')

    class Meta:
        model = ClassSchedule
        fields = ['schedule_id', 'section_id', 'day', 'time_start', 'time_end', 'classroom']
        read_only_fields = ['schedule_id']

    def validate(self, attrs):
        start_time = attrs.get('start_time')
        end_time = attrs.get('end_time')

        if start_time and end_time and start_time >= end_time:
            raise serializers.ValidationError({'end_time': 'End time must be later than start time.'})

        return attrs
