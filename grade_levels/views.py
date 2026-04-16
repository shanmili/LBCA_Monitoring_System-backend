from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from drf_yasg.utils import swagger_auto_schema
from .models import GradeLevel
from .serializers import GradeLevelSerializer


def is_admin(request):
    return (
        hasattr(request.user, 'teacher_profile')
        and request.user.teacher_profile.role == 'Admin'
    )


# ==================== GRADE LEVEL CRUD ====================

@swagger_auto_schema(
    method='get', responses={200: GradeLevelSerializer(many=True)},
    operation_description='List all grade levels'
)
@swagger_auto_schema(
    method='post', request_body=GradeLevelSerializer, responses={201: GradeLevelSerializer},
    operation_description='Create a new grade level (Admin only)'
)
@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def grade_levels_list_create(request):
    """
    GET: List all grade levels
    POST: Create a new grade level (Admin only)
    """
    if request.method == 'GET':
        grade_levels = GradeLevel.objects.all()
        serializer = GradeLevelSerializer(grade_levels, many=True)
        return Response(serializer.data)
    
    elif request.method == 'POST':
        if not is_admin(request):
            return Response({'error': 'Admin access required.'}, status=status.HTTP_403_FORBIDDEN)
        
        serializer = GradeLevelSerializer(data=request.data)
        if serializer.is_valid():
            grade_level = serializer.save()
            return Response(
                GradeLevelSerializer(grade_level).data,
                status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@swagger_auto_schema(
    method='get', responses={200: GradeLevelSerializer},
    operation_description='Retrieve a single grade level by ID'
)
@swagger_auto_schema(
    method='put', request_body=GradeLevelSerializer, responses={200: GradeLevelSerializer},
    operation_description='Update a grade level (Admin only)'
)
@swagger_auto_schema(
    method='patch', request_body=GradeLevelSerializer, responses={200: GradeLevelSerializer},
    operation_description='Partially update a grade level (Admin only)'
)
@swagger_auto_schema(
    method='delete', responses={204: 'No content'},
    operation_description='Delete a grade level (Admin only)'
)
@api_view(['GET', 'PUT', 'PATCH', 'DELETE'])
@permission_classes([IsAuthenticated])
def grade_level_detail(request, grade_level_id):
    """
    GET: Retrieve a single grade level
    PUT: Update a grade level (Admin only)
    PATCH: Partially update a grade level (Admin only)
    DELETE: Delete a grade level (Admin only)
    """
    try:
        grade_level = GradeLevel.objects.get(grade_level_id=grade_level_id)
    except GradeLevel.DoesNotExist:
        return Response({'error': 'Grade level not found.'}, status=status.HTTP_404_NOT_FOUND)
    
    if request.method == 'GET':
        serializer = GradeLevelSerializer(grade_level)
        return Response(serializer.data)
    
    elif request.method in ['PUT', 'PATCH']:
        if not is_admin(request):
            return Response({'error': 'Admin access required.'}, status=status.HTTP_403_FORBIDDEN)
        
        serializer = GradeLevelSerializer(grade_level, data=request.data, partial=(request.method == 'PATCH'))
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    elif request.method == 'DELETE':
        if not is_admin(request):
            return Response({'error': 'Admin access required.'}, status=status.HTTP_403_FORBIDDEN)
        
        grade_level.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
