from rest_framework import serializers
from .models import Student, StudentEnrollment
from django.contrib.auth.models import User
from django.db import IntegrityError, transaction
import uuid

class StudentEnrollmentSerializer(serializers.ModelSerializer):
    # Student fields nested inside enrollment form
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
            'grade_level', 'section', 'school_year', 'enrolled_by', 'is_active',
        ]

    def _generate_temporary_username(self):
        return f"tmp_student_{uuid.uuid4().hex[:16]}"

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

        try:
            with transaction.atomic():
                # Create a temporary user first, then rename it to S### once student ID exists.
                temp_username = self._generate_temporary_username()
                user = User.objects.create_user(
                    username=temp_username,
                    password=temp_username
                )

                # Create student record
                student = Student.objects.create(
                    user=user,
                    created_by=validated_data.get('enrolled_by'),
                    **student_data
                )

                student_login_id = f"S{student.id:03d}"
                if User.objects.filter(username=student_login_id).exclude(pk=user.pk).exists():
                    raise serializers.ValidationError({
                        'detail': f'Generated Student ID {student_login_id} is already used as a username.'
                    })

                user.username = student_login_id
                user.set_password(student_login_id)
                user.save(update_fields=['username', 'password'])

                # Create enrollment record
                enrollment = StudentEnrollment.objects.create(
                    student=student,
                    **validated_data
                )

                return enrollment
        except IntegrityError as exc:
            raise serializers.ValidationError({
                'detail': 'Unable to create enrollment due to related data constraints. Verify referenced IDs and try again.'
            }) from exc


class StudentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Student
        fields = '__all__'