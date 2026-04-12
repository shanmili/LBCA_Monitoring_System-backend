from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from rest_framework.renderers import JSONRenderer
from django.contrib.auth import authenticate
from .models import Parent
from .serializers import ParentSerializer


# ==================== AUTHENTICATION ====================

@api_view(['POST'])
@permission_classes([AllowAny])
def parent_login(request):
    """
    Parent login using student ID as both username and password
    
    The student ID is both the username and default password for first login.
    Example:
    {
        "username": "STU001",
        "password": "STU001"
    }
    """
    username = request.data.get('username')
    password = request.data.get('password')
    
    # Student ID is used as both username and password
    if not username or not password:
        return Response(
            {'error': 'Username and password are required'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        # Try to find parent by student ID (username should be student ID)
        parent = Parent.objects.select_related('student__user').get(
            student__user__username=username
        )
        
        # Authenticate using Django's User model
        user = authenticate(username=username, password=password)
        
        if user is None:
            return Response(
                {'error': 'Invalid credentials. Student ID (username) and password do not match.'},
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        # Create or get token
        token, created = Token.objects.get_or_create(user=user)
        
        return Response({
            'message': 'Parent login successful',
            'token': token.key,
            'username': user.username,
            'parent_id': parent.id,
            'student_id': parent.student.id,
            'student_name': f"{parent.student.first_name} {parent.student.last_name}",
            'parent_name': f"{parent.first_name} {parent.last_name}",
            'relationship': parent.relationship,
            'email': parent.email,
            'phone': parent.phone
        }, status=status.HTTP_200_OK)
        
    except Parent.DoesNotExist:
        return Response(
            {'error': 'Parent account not found for this student ID'},
            status=status.HTTP_401_UNAUTHORIZED
        )


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def parent_logout(request):
    """
    Parent logout - delete authentication token
    """
    request.user.auth_token.delete()
    return Response({'message': 'Logout successful'})


# ==================== PROFILE MANAGEMENT ====================

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_parent_profile(request):
    """
    Get current parent's profile
    """
    try:
        parent = Parent.objects.select_related('student').get(student__user=request.user)
        serializer = ParentSerializer(parent)
        return Response(serializer.data)
    except Parent.DoesNotExist:
        return Response(
            {'error': 'Parent profile not found'},
            status=status.HTTP_404_NOT_FOUND
        )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_student_info(request):
    """
    Get student information for the parent
    """
    try:
        parent = Parent.objects.select_related('student').get(student__user=request.user)
        student = parent.student
        active_enrollment = (
            student.enrollments.select_related('grade_level', 'section')
            .filter(is_active=True)
            .first()
        )
        
        return Response({
            'student_id': student.id,
            'first_name': student.first_name,
            'middle_name': student.middle_name,
            'last_name': student.last_name,
            'birth_date': student.birth_date,
            'gender': student.gender,
            'address': student.address,
            'grade_level': active_enrollment.grade_level.level if active_enrollment else None,
            'section': active_enrollment.section.name if active_enrollment else None,
            'created_at': student.created_at,
            'updated_at': student.updated_at
        })
    except Parent.DoesNotExist:
        return Response(
            {'error': 'Parent profile not found'},
            status=status.HTTP_404_NOT_FOUND
        )
