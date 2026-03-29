from rest_framework import serializers
from .models import Student, StudentEnrollment
from django.contrib.auth.models import User


class StudentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Student
        fields = '__all__'


class StudentEnrollmentSerializer(serializers.ModelSerializer):
    first_name = serializers.CharField(write_only=True)
    middle_name = serializers.CharField(write_only=True, required=False, allow_blank=True)
    last_name = serializers.CharField(write_only=True)
    birth_date = serializers.CharField(write_only=True)
    gender = serializers.ChoiceField(choices=['Male', 'Female'], write_only=True)
    address = serializers.CharField(write_only=True)
    guardian_first_name = serializers.CharField(write_only=True)
    guardian_mid_name = serializers.CharField(write_only=True, required=False, allow_blank=True)
    guardian_last_name = serializers.CharField(write_only=True)
    guardian_contact = serializers.CharField(write_only=True)
    relationship = serializers.ChoiceField(choices=['Parent', 'Guardian', 'Other'], write_only=True)

    class Meta:
        model = StudentEnrollment
        fields = [
            # Student fields
            'first_name', 'middle_name', 'last_name', 'birth_date',
            'gender', 'address', 'guardian_first_name', 'guardian_mid_name',
            'guardian_last_name', 'guardian_contact', 'relationship',
            # Enrollment fields
            'grade_level', 'section', 'school_year', 'is_active',
        ]

    def create(self, validated_data):
        # Extract student fields
        student_data = {
            'first_name': validated_data.pop('first_name'),
            'middle_name': validated_data.pop('middle_name', None),
            'last_name': validated_data.pop('last_name'),
            'birth_date': validated_data.pop('birth_date'),
            'gender': validated_data.pop('gender'),
            'address': validated_data.pop('address'),
            'guardian_first_name': validated_data.pop('guardian_first_name'),
            'guardian_mid_name': validated_data.pop('guardian_mid_name', None),
            'guardian_last_name': validated_data.pop('guardian_last_name'),
            'guardian_contact': validated_data.pop('guardian_contact'),
            'relationship': validated_data.pop('relationship'),
        }

        logged_in_user = self.context['request'].user

        # Get teacher profile if teacher, None if admin
        teacher_profile = getattr(logged_in_user, 'teacher_profile', None)

        # Auto create user account for the student
        user = User.objects.create_user(
            username=f"{student_data['first_name'].lower()}.{student_data['last_name'].lower()}",
            password="defaultpassword123"
        )

        # Create student record
        student = Student.objects.create(
            user=user,
            created_by=logged_in_user,
            **student_data
        )

        # Create enrollment record
        enrollment = StudentEnrollment.objects.create(
            student=student,
            enrolled_by=teacher_profile,  # FK to teachers table, None if admin
            **validated_data
        )

        return enrollment