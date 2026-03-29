from rest_framework import serializers
from .models import Student, StudentEnrollment
from django.contrib.auth.models import User


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
    # Write-only fields for creating enrollments
    student = serializers.IntegerField(write_only=True, required=False)
    first_name = serializers.CharField(write_only=True, required=False, allow_blank=True)
    middle_name = serializers.CharField(write_only=True, required=False, allow_blank=True)
    last_name = serializers.CharField(write_only=True, required=False, allow_blank=True)
    birth_date = serializers.CharField(write_only=True, required=False, allow_blank=True)
    gender = serializers.ChoiceField(choices=['Male', 'Female'], write_only=True, required=False, allow_blank=True)
    address = serializers.CharField(write_only=True, required=False, allow_blank=True)
    guardian_first_name = serializers.CharField(write_only=True, required=False, allow_blank=True)
    guardian_mid_name = serializers.CharField(write_only=True, required=False, allow_blank=True)
    guardian_last_name = serializers.CharField(write_only=True, required=False, allow_blank=True)
    guardian_contact = serializers.CharField(write_only=True, required=False, allow_blank=True)
    relationship = serializers.ChoiceField(choices=['Parent', 'Guardian', 'Other'], write_only=True, required=False, allow_blank=True)

    class Meta:
        model = StudentEnrollment
        fields = [
            'id', 'grade_level', 'section', 'school_year', 'is_active', 'enrollment_date', 'enrolled_by',
            'student', 'first_name', 'middle_name', 'last_name', 'birth_date', 'gender', 'address',
            'guardian_first_name', 'guardian_mid_name', 'guardian_last_name', 'guardian_contact', 'relationship',
        ]
        read_only_fields = ['id', 'enrollment_date']

    def create(self, validated_data):
        logged_in_user = self.context['request'].user
        student_id = validated_data.pop('student', None)
        
        # Get teacher profile if teacher
        teacher_profile = getattr(logged_in_user, 'teacher_profile', None)
        
        # Case 1: Enrolling an existing student by ID
        if student_id:
            try:
                student = Student.objects.get(pk=student_id)
            except Student.DoesNotExist:
                raise serializers.ValidationError({'student': 'Student not found.'})
        else:
            # Case 2: Create a new student and enroll them
            student_data = {
                'first_name': validated_data.pop('first_name', ''),
                'middle_name': validated_data.pop('middle_name', ''),
                'last_name': validated_data.pop('last_name', ''),
                'birth_date': validated_data.pop('birth_date', None),
                'gender': validated_data.pop('gender', 'Male'),
                'address': validated_data.pop('address', ''),
                'guardian_first_name': validated_data.pop('guardian_first_name', ''),
                'guardian_mid_name': validated_data.pop('guardian_mid_name', ''),
                'guardian_last_name': validated_data.pop('guardian_last_name', ''),
                'guardian_contact': validated_data.pop('guardian_contact', ''),
                'relationship': validated_data.pop('relationship', 'Parent'),
            }

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

        # Remove any remaining student fields from validated_data
        for field in ['first_name', 'middle_name', 'last_name', 'birth_date', 'gender', 
                      'address', 'guardian_first_name', 'guardian_mid_name', 
                      'guardian_last_name', 'guardian_contact', 'relationship']:
            validated_data.pop(field, None)

        # Create enrollment record for the student
        validated_data['student'] = student
        validated_data['enrolled_by'] = teacher_profile
        
        return StudentEnrollment.objects.create(**validated_data)