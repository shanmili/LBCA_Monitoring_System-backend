from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from .models import Student, StudentEnrollment
from .serializers import StudentSerializer, StudentEnrollmentSerializer


def is_admin(request):
    """Check if user is admin"""
    return (
        hasattr(request.user, 'teacher_profile')
        and request.user.teacher_profile.role == 'Admin'
    ) or request.user.is_staff


# ==================== AUTHENTICATION ====================

@api_view(['POST'])
@permission_classes([AllowAny])
def login(request):
    """
    Student/Teacher/Admin login using username and password
    """
    username = request.data.get('username')
    password = request.data.get('password')
    
    user = authenticate(username=username, password=password)
    
    if user is not None:
        token, created = Token.objects.get_or_create(user=user)
        
        role = "Admin" if user.is_staff else ("Teacher" if hasattr(user, 'teacher_profile') else "Student")
        
        return Response({
            'message': 'Login successful',
            'token': token.key,
            'username': user.username,
            'role': role
        }, status=status.HTTP_200_OK)
    
    return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)


# ==================== STUDENTS CRUD ====================

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_students(request):
    """
    List all students.
    Accessible by Admin and Teacher.
    """
    students = Student.objects.all()
    serializer = StudentSerializer(students, many=True)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_student(request, student_id):
    """
    Retrieve a single student by ID.
    """
    try:
        student = Student.objects.get(pk=student_id)
        serializer = StudentSerializer(student)
        return Response(serializer.data)
    except Student.DoesNotExist:
        return Response({'error': 'Student not found.'}, status=status.HTTP_404_NOT_FOUND)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_student(request):
    """
    Create a new student. Admin only.
    User account is auto-created from first_name and last_name.
    """
    if not is_admin(request):
        return Response({'error': 'Admin access required.'}, status=status.HTTP_403_FORBIDDEN)
    
    serializer = StudentSerializer(data=request.data)
    if serializer.is_valid():
        # Save with created_by automatically set to current user
        student = serializer.save(created_by=request.user)
        student_data = serializer.data
        
        return Response(
            {
                'message': 'Student created successfully.',
                'student': student_data
            },
            status=status.HTTP_201_CREATED
        )
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['PUT', 'PATCH'])
@permission_classes([IsAuthenticated])
def update_student(request, student_id):
    """
    Update a student. Admin only.
    """
    if not is_admin(request):
        return Response({'error': 'Admin access required.'}, status=status.HTTP_403_FORBIDDEN)
    
    try:
        student = Student.objects.get(pk=student_id)
    except Student.DoesNotExist:
        return Response({'error': 'Student not found.'}, status=status.HTTP_404_NOT_FOUND)
    
    serializer = StudentSerializer(student, data=request.data, partial=True)
    if serializer.is_valid():
        updated = serializer.save()
        return Response(
            {
                'message': 'Student updated successfully.',
                'student': StudentSerializer(updated).data
            }
        )
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_student(request, student_id):
    """
    Delete a student. Admin only.
    """
    if not is_admin(request):
        return Response({'error': 'Admin access required.'}, status=status.HTTP_403_FORBIDDEN)
    
    try:
        student = Student.objects.get(pk=student_id)
        student.delete()
        return Response({'message': 'Student deleted successfully.'})
    except Student.DoesNotExist:
        return Response({'error': 'Student not found.'}, status=status.HTTP_404_NOT_FOUND)


# ==================== ENROLLMENTS CRUD ====================

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_enrollments(request):
    """
    List all student enrollments with student names.
    Accessible by Admin and Teacher.
    """
    try:
        enrollments = StudentEnrollment.objects.all()
        data = []
        for enrollment in enrollments:
            data.append({
                'id': enrollment.id,
                'student_name': f"{enrollment.student.first_name} {enrollment.student.last_name}",
                'student_id': enrollment.student.id,
                'grade_level_id': enrollment.grade_level_id,
                'section_id': enrollment.section_id,
                'school_year_id': enrollment.school_year_id,
                'is_active': enrollment.is_active,
                'enrollment_date': enrollment.enrollment_date.isoformat() if enrollment.enrollment_date else None,
                'enrolled_by_id': enrollment.enrolled_by.teacher_id if enrollment.enrolled_by else None,
            })
        return Response(data)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_enrollment(request, enrollment_id):
    """
    Retrieve a single enrollment by ID with student name.
    """
    try:
        enrollment = StudentEnrollment.objects.get(pk=enrollment_id)
        data = {
            'id': enrollment.id,
            'student_name': f"{enrollment.student.first_name} {enrollment.student.last_name}",
            'student_id': enrollment.student.id,
            'student': {
                'id': enrollment.student.id,
                'first_name': enrollment.student.first_name,
                'middle_name': enrollment.student.middle_name,
                'last_name': enrollment.student.last_name,
                'birth_date': str(enrollment.student.birth_date) if enrollment.student.birth_date else None,
                'gender': enrollment.student.gender,
                'address': enrollment.student.address,
                'guardian_first_name': enrollment.student.guardian_first_name,
                'guardian_mid_name': enrollment.student.guardian_mid_name,
                'guardian_last_name': enrollment.student.guardian_last_name,
                'guardian_contact': enrollment.student.guardian_contact,
                'relationship': enrollment.student.relationship,
            },
            'enrollment': {
                'grade_level_id': enrollment.grade_level_id,
                'section_id': enrollment.section_id,
                'school_year_id': enrollment.school_year_id,
                'is_active': enrollment.is_active,
                'enrollment_date': enrollment.enrollment_date.isoformat() if enrollment.enrollment_date else None,
                'enrolled_by_id': enrollment.enrolled_by.teacher_id if enrollment.enrolled_by else None,
            }
        }
        return Response(data)
    except StudentEnrollment.DoesNotExist:
        return Response({'error': 'Enrollment not found.'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_enrollment(request):
    """
    Create a new student enrollment. Admin and Teacher only.
    
    TWO FLOWS:
    1. EXISTING STUDENT - Enroll by student ID:
       {
           "student": 16,
           "grade_level": 1,
           "section": 1,
           "school_year": 1
       }
       Personal data pulled from Student table.
    
    2. NEW STUDENT - Create student & enroll:
       {
           "first_name": "John",
           "last_name": "Doe",
           "birth_date": "2010-01-15",
           "gender": "Male",
           "address": "123 Main St",
           "guardian_first_name": "Jane",
           "guardian_last_name": "Doe",
           "guardian_contact": "555-1234",
           "relationship": "Parent",
           "grade_level": 1,
           "section": 1,
           "school_year": 1
       }
       Creates Student record, then enrolls them.
    """
    if not (is_admin(request) or hasattr(request.user, 'teacher_profile')):
        return Response({'error': 'Access denied.'}, status=status.HTTP_403_FORBIDDEN)
    
    serializer = StudentEnrollmentSerializer(data=request.data, context={'request': request})
    if serializer.is_valid():
        enrollment = serializer.save()
        return Response(
            {
                'message': 'Enrollment created successfully.',
                'enrollment': StudentEnrollmentSerializer(enrollment).data
            },
            status=status.HTTP_201_CREATED
        )
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['PUT', 'PATCH'])
@permission_classes([IsAuthenticated])
def update_enrollment(request, enrollment_id):
    """
    Update an enrollment. Admin and Teacher only.
    """
    if not (is_admin(request) or hasattr(request.user, 'teacher_profile')):
        return Response({'error': 'Access denied.'}, status=status.HTTP_403_FORBIDDEN)
    
    try:
        enrollment = StudentEnrollment.objects.get(pk=enrollment_id)
    except StudentEnrollment.DoesNotExist:
        return Response({'error': 'Enrollment not found.'}, status=status.HTTP_404_NOT_FOUND)
    
    serializer = StudentEnrollmentSerializer(enrollment, data=request.data, partial=True)
    if serializer.is_valid():
        updated = serializer.save()
        return Response(
            {
                'message': 'Enrollment updated successfully.',
                'enrollment': StudentEnrollmentSerializer(updated).data
            }
        )
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_enrollment(request, enrollment_id):
    """
    Delete an enrollment. Admin only.
    """
    if not is_admin(request):
        return Response({'error': 'Admin access required.'}, status=status.HTTP_403_FORBIDDEN)
    
    try:
        enrollment = StudentEnrollment.objects.get(pk=enrollment_id)
        enrollment.delete()
        return Response({'message': 'Enrollment deleted successfully.'})
    except StudentEnrollment.DoesNotExist:
        return Response({'error': 'Enrollment not found.'}, status=status.HTTP_404_NOT_FOUND)