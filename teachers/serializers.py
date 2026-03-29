from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Teacher  # Import Teacher from models

class TeacherSerializer(serializers.ModelSerializer):
    """Serializer for viewing teacher data"""
    username = serializers.CharField(source='user.username', read_only=True)
    
    class Meta:
        model = Teacher
        fields = ['teacher_id', 'username', 'email', 'first_name', 'middle_name', 
                  'last_name', 'contact_number', 'role', 'status', 'is_first_login']
        read_only_fields = ['teacher_id', 'created_at', 'updated_at']

class AdminRegisterSerializer(serializers.ModelSerializer):
    """Admin self-registration - username auto-generated"""
    password = serializers.CharField(write_only=True, min_length=6)
    password_confirm = serializers.CharField(write_only=True)
    
    class Meta:
        model = Teacher
        fields = ['email', 'password', 'password_confirm', 'first_name', 
                  'middle_name', 'last_name', 'contact_number']
    
    def validate(self, data):
        if data['password'] != data['password_confirm']:
            raise serializers.ValidationError({"password": "Passwords do not match"})
        return data
    
    def create(self, validated_data):
        validated_data.pop('password_confirm')
        password = validated_data.pop('password')
        
        # Auto-generate admin username
        admin_count = Teacher.objects.filter(role='Admin').count()
        next_number = admin_count + 1
        username = f"ADMIN{next_number:03d}"
        
        # Create Django User
        user = User.objects.create_user(
            username=username,
            email=validated_data.get('email', ''),
            password=password
        )
        
        # Create Teacher
        teacher = Teacher(
            user=user,
            email=validated_data.get('email', ''),
            first_name=validated_data.get('first_name', ''),
            middle_name=validated_data.get('middle_name', ''),
            last_name=validated_data.get('last_name', ''),
            contact_number=validated_data.get('contact_number', ''),
            role='Admin',
            is_first_login=True
        )
        teacher.save()
        
        return teacher

class TeacherCreateSerializer(serializers.ModelSerializer):
    """Admin creates teacher account - username auto-generated"""
    class Meta:
        model = Teacher
        fields = []
    
    def create(self, validated_data):
        # Get the logged-in admin's Teacher instance
        admin_teacher = self.context.get('request').user.teacher_profile
        
        # Get next teacher number
        teacher_count = Teacher.objects.filter(role='Teacher').count()
        next_number = teacher_count + 1
        username = f"TCH{next_number:03d}"
        
        # Create Django User (username = TCH001, password = same)
        user = User.objects.create_user(
            username=username,
            password=username
        )
        
        # Create Teacher
        teacher = Teacher(
            user=user,
            role="Teacher",
            is_first_login=True,
            created_by=admin_teacher
        )
        teacher.save()
        
        return {
            'teacher_id': teacher.teacher_id,
            'username': username,
            'password': username,
            'is_first_login': True
        }

class TeacherUpdateSerializer(serializers.ModelSerializer):
    """Teacher updates their own profile"""
    new_password = serializers.CharField(write_only=True, required=False, min_length=6)
    username = serializers.CharField(source='user.username', read_only=True)
    
    class Meta:
        model = Teacher
        fields = ['first_name', 'middle_name', 'last_name', 'email', 'contact_number', 'new_password', 'username']
    
    def update(self, instance, validated_data):
        # Update Teacher fields
        if 'first_name' in validated_data:
            instance.first_name = validated_data['first_name']
        if 'middle_name' in validated_data:
            instance.middle_name = validated_data['middle_name']
        if 'last_name' in validated_data:
            instance.last_name = validated_data['last_name']
        if 'email' in validated_data:
            instance.email = validated_data['email']
            instance.user.email = validated_data['email']
        if 'contact_number' in validated_data:
            instance.contact_number = validated_data['contact_number']
        
        # Update password if provided
        if 'new_password' in validated_data:
            instance.user.set_password(validated_data['new_password'])
            instance.user.save()
            instance.is_first_login = False
        
        instance.save()
        instance.user.save()
        return instance