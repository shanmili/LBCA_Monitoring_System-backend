from rest_framework import status, viewsets
from rest_framework.decorators import api_view, permission_classes, action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate
from drf_yasg.utils import swagger_auto_schema
from .models import Teacher, TeacherAssignment
from .serializers import (
    TeacherSerializer, AdminRegisterSerializer,
    TeacherCreateSerializer, TeacherUpdateSerializer,
    TeacherAssignmentSerializer
)

# ==================== AUTHENTICATION ====================

@swagger_auto_schema(method='post', request_body=AdminRegisterSerializer)
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

@swagger_auto_schema(method='post')
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

@swagger_auto_schema(method='post')
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

@swagger_auto_schema(method='post')
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def teacher_logout(request):
    """
    Logout - delete authentication token
    """
    request.user.auth_token.delete()
    return Response({'message': 'Logout successful'})

# ==================== PROFILE MANAGEMENT ====================

@swagger_auto_schema(method='get', responses={200: TeacherSerializer})
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_teacher_profile(request):
    """
    Get current teacher's profile
    """
    teacher = request.user.teacher_profile
    serializer = TeacherSerializer(teacher)
    return Response(serializer.data)

@swagger_auto_schema(method='put', request_body=TeacherUpdateSerializer)
@swagger_auto_schema(method='patch', request_body=TeacherUpdateSerializer)
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

class TeacherViewSet(viewsets.ModelViewSet):
    """
    TeacherViewSet provides CRUD operations for teacher management (Admin only).
    
    Endpoints:
    - GET    /api/teachers/                    List all teachers
    - POST   /api/teachers/                    Create teacher (auto-generates username)
    - GET    /api/teachers/{id}/               Retrieve teacher
    - PUT    /api/teachers/{id}/               Full update teacher
    - PATCH  /api/teachers/{id}/               Partial update teacher
    - DELETE /api/teachers/{id}/               Deactivate teacher
    - PATCH  /api/teachers/{id}/reactivate/   Reactivate teacher
    """
    queryset = Teacher.objects.all()
    serializer_class = TeacherSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = 'teacher_id'
    
    def get_serializer_class(self):
        if self.action == 'create':
            return TeacherCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return TeacherUpdateSerializer
        return TeacherSerializer
    
    def check_admin_permission(self):
        """Check if current user is Admin"""
        if self.request.user.teacher_profile.role != 'Admin':
            raise PermissionError('Admin access required')
    
    def list(self, request, *args, **kwargs):
        """List all teachers (Admin only)"""
        self.check_admin_permission()
        return super().list(request, *args, **kwargs)
    
    def create(self, request, *args, **kwargs):
        """Create teacher account (Admin only). Auto-generates username: TCH001, TCH002, etc."""
        self.check_admin_permission()
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        result = serializer.create(serializer.validated_data)
        
        return Response({
            'message': 'Teacher account created successfully',
            'teacher_id': result['teacher_id'],
            'username': result['username'],
            'password': result['password'],
            'is_first_login': True
        }, status=status.HTTP_201_CREATED)
    
    def retrieve(self, request, *args, **kwargs):
        """Retrieve a single teacher"""
        return super().retrieve(request, *args, **kwargs)
    
    def update(self, request, *args, **kwargs):
        """Full update teacher (Admin only)"""
        self.check_admin_permission()
        return super().update(request, *args, **kwargs)
    
    def partial_update(self, request, *args, **kwargs):
        """Partial update teacher (Admin only)"""
        self.check_admin_permission()
        return super().partial_update(request, *args, **kwargs)
    
    def destroy(self, request, *args, **kwargs):
        """Soft delete (deactivate) teacher (Admin only)"""
        self.check_admin_permission()
        teacher = self.get_object()
        teacher.status = 'Inactive'
        teacher.save()
        
        return Response({
            'message': f'Teacher {teacher.user.username} deactivated successfully',
            'teacher_id': teacher.teacher_id,
            'username': teacher.user.username,
            'status': teacher.status
        }, status=status.HTTP_200_OK)
    
    @action(detail=True, methods=['patch'], permission_classes=[IsAuthenticated])
    def reactivate(self, request, teacher_id=None):
        """Reactivate teacher (Admin only)"""
        self.check_admin_permission()
        teacher = self.get_object()
        teacher.status = 'Active'
        teacher.save()
        
        return Response({
            'message': f'Teacher {teacher.user.username} reactivated successfully',
            'teacher_id': teacher.teacher_id,
            'username': teacher.user.username,
            'status': teacher.status
        }, status=status.HTTP_200_OK)


# ==================== TEACHER PROFILE ====================

@swagger_auto_schema(method='get', responses={200: TeacherSerializer})
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_teacher_profile(request):
    """
    Get current teacher's profile
    """
    teacher = request.user.teacher_profile
    serializer = TeacherSerializer(teacher)
    return Response(serializer.data)

@swagger_auto_schema(method='put', request_body=TeacherUpdateSerializer)
@swagger_auto_schema(method='patch', request_body=TeacherUpdateSerializer)
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


# ==================== TEACHER ASSIGNMENTS ====================

class TeacherAssignmentViewSet(viewsets.ModelViewSet):
    """
    TeacherAssignmentViewSet provides CRUD operations for teacher assignments (Admin only).
    
    Endpoints:
    - GET    /api/teacher-assignments/                   List assignments (with optional filters)
    - POST   /api/teacher-assignments/                   Create assignment
    - GET    /api/teacher-assignments/{id}/              Retrieve assignment
    - PUT    /api/teacher-assignments/{id}/              Full update assignment
    - PATCH  /api/teacher-assignments/{id}/              Partial update assignment
    - DELETE /api/teacher-assignments/{id}/              Delete assignment
    
    Optional Query Parameters on List:
    - ?teacher_id=1    Filter by teacher
    - ?section_id=2    Filter by section
    - ?school_year_id=1  Filter by school year
    """
    queryset = TeacherAssignment.objects.all()
    serializer_class = TeacherAssignmentSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = 'assignment_id'
    
    def check_admin_permission(self):
        """Check if current user is Admin"""
        if self.request.user.teacher_profile.role != 'Admin':
            raise PermissionError('Admin access required')
    
    def get_queryset(self):
        """Filter assignments based on query parameters"""
        queryset = TeacherAssignment.objects.all()
        
        teacher_id = self.request.query_params.get('teacher_id')
        section_id = self.request.query_params.get('section_id')
        school_year_id = self.request.query_params.get('school_year_id')
        
        if teacher_id:
            queryset = queryset.filter(teacher__teacher_id=teacher_id)
        if section_id:
            queryset = queryset.filter(section__section_id=section_id)
        if school_year_id:
            queryset = queryset.filter(school_year__school_year_id=school_year_id)
        
        return queryset
    
    def list(self, request, *args, **kwargs):
        """List teacher assignments (optional filters)"""
        return super().list(request, *args, **kwargs)
    
    def create(self, request, *args, **kwargs):
        """Create teacher assignment (Admin only)"""
        self.check_admin_permission()
        return super().create(request, *args, **kwargs)
    
    def retrieve(self, request, *args, **kwargs):
        """Retrieve a single teacher assignment"""
        return super().retrieve(request, *args, **kwargs)
    
    def update(self, request, *args, **kwargs):
        """Full update teacher assignment (Admin only)"""
        self.check_admin_permission()
        return super().update(request, *args, **kwargs)
    
    def partial_update(self, request, *args, **kwargs):
        """Partial update teacher assignment (Admin only)"""
        self.check_admin_permission()
        return super().partial_update(request, *args, **kwargs)
    
    def destroy(self, request, *args, **kwargs):
        """Delete teacher assignment (Admin only)"""
        self.check_admin_permission()
        return super().destroy(request, *args, **kwargs)