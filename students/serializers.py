from rest_framework import serializers
from .models import Student, StudentEnrollment
from django.contrib.auth.models import User
from collections import OrderedDict


class StudentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Student
        fields = [
            'id',
            'user',
            'first_name',
            'middle_name',
            'last_name',
            'birth_date',
            'gender',
            'address',
            'guardian_first_name',
            'guardian_mid_name',
            'guardian_last_name',
            'guardian_contact',
            'relationship',
            'created_at',
            'updated_at',
            'created_by',
        ]
        read_only_fields = ['id', 'user', 'created_at', 'updated_at', 'created_by']

    def to_representation(self, instance):
        """Force exact field order"""
        ret = OrderedDict()
        ret['id'] = instance.id
        ret['user'] = instance.user.id if instance.user else None
        ret['first_name'] = instance.first_name
        ret['middle_name'] = instance.middle_name
        ret['last_name'] = instance.last_name
        ret['birth_date'] = instance.birth_date
        ret['gender'] = instance.gender
        ret['address'] = instance.address
        ret['guardian_first_name'] = instance.guardian_first_name
        ret['guardian_mid_name'] = instance.guardian_mid_name
        ret['guardian_last_name'] = instance.guardian_last_name
        ret['guardian_contact'] = instance.guardian_contact
        ret['relationship'] = instance.relationship
        ret['created_at'] = instance.created_at.isoformat() if instance.created_at else None
        ret['updated_at'] = instance.updated_at.isoformat() if instance.updated_at else None
        ret['created_by'] = instance.created_by.id if instance.created_by else None
        return ret

    def create(self, validated_data):
        """Auto-create User for Student"""
        first_name = validated_data.get('first_name')
        last_name = validated_data.get('last_name')
        
        # Generate username from first and last name
        base_username = f"{first_name.lower()}.{last_name.lower()}"
        username = base_username
        counter = 1
        
        # Ensure username is unique
        while User.objects.filter(username=username).exists():
            username = f"{base_username}{counter}"
            counter += 1
        
        # Auto-create User account for the student
        user = User.objects.create_user(
            username=username,
            first_name=first_name,
            last_name=last_name,
            password="defaultPassword123!"
        )
        
        validated_data['user'] = user
        return super().create(validated_data)


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

        # Auto create user account for the student with unique username
        first_name = student_data['first_name']
        last_name = student_data['last_name']
        base_username = f"{first_name.lower()}.{last_name.lower()}"
        username = base_username
        counter = 1
        
        # Ensure username is unique
        while User.objects.filter(username=username).exists():
            username = f"{base_username}{counter}"
            counter += 1
        
        user = User.objects.create_user(
            username=username,
            first_name=first_name,
            last_name=last_name,
            password="defaultPassword123!"
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