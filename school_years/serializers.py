from rest_framework import serializers
from .models import SchoolYear


class SchoolYearSerializer(serializers.ModelSerializer):
    class Meta:
        model = SchoolYear
        fields = ['school_year_id', 'year', 'is_current', 'start_date', 'end_date']
        read_only_fields = ['school_year_id']

    def validate_year(self, value):
        """Ensure year follows YYYY-YYYY format."""
        import re
        if not re.match(r'^\d{4}-\d{4}$', value):
            raise serializers.ValidationError("Year must follow the format YYYY-YYYY (e.g. 2024-2025).")
        parts = value.split('-')
        if int(parts[1]) != int(parts[0]) + 1:
            raise serializers.ValidationError("The second year must be exactly one year after the first.")
        return value

    def validate(self, data):
        start = data.get('start_date')
        end = data.get('end_date')
        if start and end and end <= start:
            raise serializers.ValidationError({"end_date": "End date must be after start date."})
        return data
