from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate
from .models import Teacher, TeacherAssignment
from .serializers import (
    TeacherSerializer, AdminRegisterSerializer,
    TeacherCreateSerializer, TeacherUpdateSerializer,
    TeacherAssignmentSerializer
)

# ==================== AUTHENTICATION ====================

@api_view(['POST'])
@permission_classes([AllowAny])
def admin_register(request):
    """
    Admin self-registration
    Auto-generates username: ADMIN001, ADMIN002, etc.
    """
    serializer = AdminRegisterSerializer(data=request.data)
    if serializer.is_valid():
        teacher = serializer.save()
        token, created = Token.objects.get_or_create(user=teacher.user)
        
        return Response({
            'message': 'Admin account created successfully',
            'token': token.key,
            'username': teacher.user.username,
            'teacher_id': teacher.teacher_id,
            'role': teacher.role,
            'first_name': teacher.first_name,
            'last_name': teacher.last_name,
            'is_first_login': teacher.is_first_login
        }, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([AllowAny])
def admin_login(request):
    """
    Admin-only login using username (ADMIN001, ADMIN002, etc.) and password
    """
    username = request.data.get('username')
    password = request.data.get('password')
    
    # Authenticate using Django's User model
    user = authenticate(username=username, password=password)
    
    if user and hasattr(user, 'teacher_profile'):
        teacher = user.teacher_profile
        
        # Check if user is an admin
        if teacher.role != 'Admin':
            return Response({'error': 'Admin access required. You are not an admin.'}, status=status.HTTP_403_FORBIDDEN)
        
        # Check if account is active
        if teacher.status != 'Active':
            return Response({'error': 'Account is deactivated. Contact system administrator.'}, status=status.HTTP_401_UNAUTHORIZED)
        
        token, created = Token.objects.get_or_create(user=user)
        
        return Response({
            'message': 'Admin login successful',
            'token': token.key,
            'username': user.username,
            'teacher_id': teacher.teacher_id,
            'role': teacher.role,
            'first_name': teacher.first_name,
            'last_name': teacher.last_name,
            'is_first_login': teacher.is_first_login
        })
    
    return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)

@api_view(['POST'])
@permission_classes([AllowAny])
def teacher_login(request):
    """
    Teacher/Admin login using username (ADMIN001, TCH001) and password
    """
    username = request.data.get('username')
    password = request.data.get('password')
    
    # Authenticate using Django's User model
    user = authenticate(username=username, password=password)
    
    if user and hasattr(user, 'teacher_profile'):
        teacher = user.teacher_profile
    
        # Check if account is active
        if teacher.status != 'Active':
            return Response({'error': 'Account is deactivated. Contact admin.'}, status=status.HTTP_401_UNAUTHORIZED)
        
        token, created = Token.objects.get_or_create(user=user)
        
        return Response({
            'message': 'Login successful',
            'token': token.key,
            'username': user.username,
            'teacher_id': teacher.teacher_id,
            'role': teacher.role,
            'first_name': teacher.first_name,
            'last_name': teacher.last_name,
            'is_first_login': teacher.is_first_login
        })
    
    return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def teacher_logout(request):
    """
    Logout - delete authentication token
    """
    request.user.auth_token.delete()
    return Response({'message': 'Logout successful'})

# ==================== PROFILE MANAGEMENT ====================

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_teacher_profile(request):
    """
    Get current teacher's profile
    """
    teacher = request.user.teacher_profile
    serializer = TeacherSerializer(teacher)
    return Response(serializer.data)

@api_view(['PUT', 'PATCH'])
@permission_classes([IsAuthenticated])
def update_teacher_profile(request):
    """
    Update own profile (name, email, contact, password)
    """
    teacher = request.user.teacher_profile
    serializer = TeacherUpdateSerializer(teacher, data=request.data, partial=True)
    
    if serializer.is_valid():
        serializer.save()
        
        # Get updated teacher data
        updated_teacher = Teacher.objects.get(teacher_id=teacher.teacher_id)
        
        return Response({
            'message': 'Profile updated successfully',
            'teacher': TeacherSerializer(updated_teacher).data
        })
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# ==================== ADMIN ONLY ====================

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_teacher(request):
    """
    Admin creates teacher account
    Auto-generates username: TCH001, TCH002, etc.
    Password = same as username
    """
    # Check if current user is Admin
    if request.user.teacher_profile.role != 'Admin':
        return Response({'error': 'Admin access required'}, status=status.HTTP_403_FORBIDDEN)
    
    serializer = TeacherCreateSerializer(data=request.data, context={'request': request})
    if serializer.is_valid():
        result = serializer.create(serializer.validated_data)
        
        return Response({
            'message': 'Teacher account created successfully',
            'teacher_id': result['teacher_id'],
            'username': result['username'],
            'password': result['password'],
            'is_first_login': True
        }, status=status.HTTP_201_CREATED)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_teachers(request):
    """
    List all teachers (Admin only)
    """
    if request.user.teacher_profile.role != 'Admin':
        return Response({'error': 'Admin access required'}, status=status.HTTP_403_FORBIDDEN)
    
    teachers = Teacher.objects.all()
    serializer = TeacherSerializer(teachers, many=True)
    return Response(serializer.data)

@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_teacher(request, teacher_id):
    """
    Admin soft deletes teacher (sets status to Inactive)
    """
    # Check if current user is Admin
    if request.user.teacher_profile.role != 'Admin':
        return Response({'error': 'Admin access required'}, status=status.HTTP_403_FORBIDDEN)
    
    try:
        teacher = Teacher.objects.get(teacher_id=teacher_id)
        
        # Soft delete - only change status
        teacher.status = 'Inactive'
        teacher.save()
        
        return Response({
            'message': f'Teacher {teacher.user.username} deactivated successfully',
            'teacher_id': teacher.teacher_id,
            'username': teacher.user.username,
            'status': teacher.status
        }, status=status.HTTP_200_OK)
        
    except Teacher.DoesNotExist:
        return Response({'error': 'Teacher not found'}, status=status.HTTP_404_NOT_FOUND)

@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
def reactivate_teacher(request, teacher_id):
    """
    Admin reactivates teacher (sets status to Active)
    """
    # Check if user is Admin
    if request.user.teacher_profile.role != 'Admin':
        return Response({'error': 'Admin access required'}, status=status.HTTP_403_FORBIDDEN)
    
    try:
        teacher = Teacher.objects.get(teacher_id=teacher_id)
        
        # Reactivate
        teacher.status = 'Active'
        teacher.save()
        
        return Response({
            'message': f'Teacher {teacher.user.username} reactivated successfully',
            'teacher_id': teacher.teacher_id,
            'username': teacher.user.username,
            'status': teacher.status
        }, status=status.HTTP_200_OK)
        
    except Teacher.DoesNotExist:
        return Response({'error': 'Teacher not found'}, status=status.HTTP_404_NOT_FOUND)


# ==================== TEACHER ASSIGNMENTS ====================

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_teacher_assignments(request):
    """
    List teacher assignments.
    Optional filters: ?teacher_id=1&section_id=2&school_year_id=1
    """
    assignments = TeacherAssignment.objects.all()

    teacher_id = request.query_params.get('teacher_id')
    section_id = request.query_params.get('section_id')
    school_year_id = request.query_params.get('school_year_id')

    if teacher_id:
        assignments = assignments.filter(teacher__teacher_id=teacher_id)
    if section_id:
        assignments = assignments.filter(section__section_id=section_id)
    if school_year_id:
        assignments = assignments.filter(school_year__school_year_id=school_year_id)

    serializer = TeacherAssignmentSerializer(assignments, many=True)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_teacher_assignment(request, assignment_id):
    """
    Retrieve a single teacher assignment.
    """
    try:
        assignment = TeacherAssignment.objects.get(assignment_id=assignment_id)
    except TeacherAssignment.DoesNotExist:
        return Response({'error': 'Assignment not found.'}, status=status.HTTP_404_NOT_FOUND)

    serializer = TeacherAssignmentSerializer(assignment)
    return Response(serializer.data)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_teacher_assignment(request):
    """
    Create teacher assignment. Admin only.
    """
    if request.user.teacher_profile.role != 'Admin':
        return Response({'error': 'Admin access required'}, status=status.HTTP_403_FORBIDDEN)

    serializer = TeacherAssignmentSerializer(data=request.data)
    if serializer.is_valid():
        assignment = serializer.save()
        return Response(
            {
                'message': 'Teacher assignment created successfully.',
                'assignment': TeacherAssignmentSerializer(assignment).data,
            },
            status=status.HTTP_201_CREATED,
        )
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['PUT', 'PATCH'])
@permission_classes([IsAuthenticated])
def update_teacher_assignment(request, assignment_id):
    """
    Update teacher assignment. Admin only.
    """
    if request.user.teacher_profile.role != 'Admin':
        return Response({'error': 'Admin access required'}, status=status.HTTP_403_FORBIDDEN)

    try:
        assignment = TeacherAssignment.objects.get(assignment_id=assignment_id)
    except TeacherAssignment.DoesNotExist:
        return Response({'error': 'Assignment not found.'}, status=status.HTTP_404_NOT_FOUND)

    serializer = TeacherAssignmentSerializer(assignment, data=request.data, partial=True)
    if serializer.is_valid():
        updated_assignment = serializer.save()
        return Response(
            {
                'message': 'Teacher assignment updated successfully.',
                'assignment': TeacherAssignmentSerializer(updated_assignment).data,
            }
        )
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_teacher_assignment(request, assignment_id):
    """
    Delete teacher assignment. Admin only.
    """
    if request.user.teacher_profile.role != 'Admin':
        return Response({'error': 'Admin access required'}, status=status.HTTP_403_FORBIDDEN)

    try:
        assignment = TeacherAssignment.objects.get(assignment_id=assignment_id)
    except TeacherAssignment.DoesNotExist:
        return Response({'error': 'Assignment not found.'}, status=status.HTTP_404_NOT_FOUND)

    assignment.delete()
    return Response({'message': 'Teacher assignment deleted successfully.'}, status=status.HTTP_200_OK)