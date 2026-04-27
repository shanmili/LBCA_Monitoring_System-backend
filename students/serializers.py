from rest_framework import serializers
from .models import Student, StudentEnrollment
from django.contrib.auth.models import User
from django.db import IntegrityError, transaction
import uuid


class StudentSerializer(serializers.ModelSerializer):
    student_id = serializers.IntegerField(source='id', read_only=True)
    login_id = serializers.CharField(source='user.username', read_only=True)
    guardian_relationship = serializers.ChoiceField(source='relationship', choices=['Parent', 'Guardian', 'Other'])

    class Meta:
        model = Student
        fields = [
            'student_id',
            'login_id',
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
            'guardian_relationship',
            'created_at',
            'updated_at',
            'created_by',
        ]
        read_only_fields = ['student_id', 'login_id', 'created_at', 'updated_at', 'created_by']

    def _generate_temporary_username(self):
        return f"tmp_student_{uuid.uuid4().hex[:16]}"

    def create(self, validated_data):
        relationship = validated_data.pop('relationship')

        with transaction.atomic():
            temp_username = self._generate_temporary_username()
            user = User.objects.create_user(username=temp_username, password=temp_username)

            student = Student.objects.create(
                user=user,
                relationship=relationship,
                created_by=self.context['request'].user,
                **validated_data,
            )

            student_login_id = f"S{student.id:03d}"
            user.username = student_login_id
            user.set_password(student_login_id)
            user.save(update_fields=['username', 'password'])

            return student

    def update(self, instance, validated_data):
        relationship = validated_data.pop('relationship', None)
        for key, value in validated_data.items():
            setattr(instance, key, value)
        if relationship is not None:
            instance.relationship = relationship
        instance.save()
        return instance

class StudentEnrollmentSerializer(serializers.ModelSerializer):
    enrollment_id = serializers.IntegerField(source='id', read_only=True)
    student_id = serializers.PrimaryKeyRelatedField(source='student', queryset=Student.objects.all())
    grade_level_id = serializers.PrimaryKeyRelatedField(source='grade_level', queryset=StudentEnrollment._meta.get_field('grade_level').remote_field.model.objects.all())
    section_id = serializers.PrimaryKeyRelatedField(source='section', queryset=StudentEnrollment._meta.get_field('section').remote_field.model.objects.all())
    school_year_id = serializers.PrimaryKeyRelatedField(source='school_year', queryset=StudentEnrollment._meta.get_field('school_year').remote_field.model.objects.all())
    next_grade_level_id = serializers.PrimaryKeyRelatedField(source='next_grade_level', queryset=StudentEnrollment._meta.get_field('next_grade_level').remote_field.model.objects.all(), required=False, allow_null=True)

    class Meta:
        model = StudentEnrollment
        fields = [
            'enrollment_id',
            'student_id',
            'grade_level_id',
            'section_id',
            'school_year_id',
            'enrolled_by',
            'next_grade_level_id',
            'enrollment_date',
            'is_active',
            'end_of_year_status',
        ]
        read_only_fields = ['enrollment_date']


class StudentEnrollmentWithStudentSerializer(serializers.Serializer):
    first_name = serializers.CharField()
    middle_name = serializers.CharField(required=False, allow_blank=True)
    last_name = serializers.CharField()
    birth_date = serializers.CharField()
    gender = serializers.ChoiceField(choices=['Male', 'Female'])
    address = serializers.CharField()
    guardian_first_name = serializers.CharField()
    guardian_mid_name = serializers.CharField(required=False, allow_blank=True)
    guardian_last_name = serializers.CharField()
    guardian_contact = serializers.CharField()
    guardian_relationship = serializers.ChoiceField(choices=['Parent', 'Guardian', 'Other'])
    grade_level_id = serializers.IntegerField()
    section_id = serializers.IntegerField()
    school_year_id = serializers.IntegerField()
    next_grade_level_id = serializers.IntegerField(required=False, allow_null=True)
    is_active = serializers.BooleanField(required=False, default=True)

    def create(self, validated_data):
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
            'guardian_relationship': validated_data.pop('guardian_relationship'),
        }

        try:
            with transaction.atomic():
                student_serializer = StudentSerializer(data=student_data, context=self.context)
                student_serializer.is_valid(raise_exception=True)
                student = student_serializer.save()

                enrollment_payload = {
                    'student_id': student.id,
                    'grade_level_id': validated_data.get('grade_level_id'),
                    'section_id': validated_data.get('section_id'),
                    'school_year_id': validated_data.get('school_year_id'),
                    'next_grade_level_id': validated_data.get('next_grade_level_id'),
                    'is_active': validated_data.get('is_active', True),
                    'enrolled_by': self.context['request'].user.id,
                }
                enrollment_serializer = StudentEnrollmentSerializer(data=enrollment_payload)
                enrollment_serializer.is_valid(raise_exception=True)
                enrollment = enrollment_serializer.save(enrolled_by=self.context['request'].user)
                return {'student': student, 'enrollment': enrollment}
        except IntegrityError as exc:
            raise serializers.ValidationError(
                {'detail': 'Unable to create enrollment due to related data constraints. Verify referenced IDs and try again.'}
            ) from exc