from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .models import GradeLevel
from .serializers import GradeLevelSerializer


def is_admin(request):
    return (
        hasattr(request.user, 'teacher_profile')
        and request.user.teacher_profile.role == 'Admin'
    )


# ==================== GRADE LEVEL CRUD ====================

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_grade_levels(request):
    """
    List all grade levels.
    Accessible by Admin and Teacher.
    """
    grade_levels = GradeLevel.objects.all()
    serializer = GradeLevelSerializer(grade_levels, many=True)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_grade_level(request, grade_level_id):
    """
    Retrieve a single grade level by ID.
    """
    try:
        grade_level = GradeLevel.objects.get(grade_level_id=grade_level_id)
        serializer = GradeLevelSerializer(grade_level)
        return Response(serializer.data)
    except GradeLevel.DoesNotExist:
        return Response({'error': 'Grade level not found.'}, status=status.HTTP_404_NOT_FOUND)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_grade_level(request):
    """
    Create a new grade level. Admin only.
    """
    if not is_admin(request):
        return Response({'error': 'Admin access required.'}, status=status.HTTP_403_FORBIDDEN)

    serializer = GradeLevelSerializer(data=request.data)
    if serializer.is_valid():
        grade_level = serializer.save()
        return Response(
            {
                'message': 'Grade level created successfully.',
                'grade_level': GradeLevelSerializer(grade_level).data
            },
            status=status.HTTP_201_CREATED
        )
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['PUT', 'PATCH'])
@permission_classes([IsAuthenticated])
def update_grade_level(request, grade_level_id):
    """
    Update a grade level. Admin only.
    """
    if not is_admin(request):
        return Response({'error': 'Admin access required.'}, status=status.HTTP_403_FORBIDDEN)

    try:
        grade_level = GradeLevel.objects.get(grade_level_id=grade_level_id)
    except GradeLevel.DoesNotExist:
        return Response({'error': 'Grade level not found.'}, status=status.HTTP_404_NOT_FOUND)

    serializer = GradeLevelSerializer(grade_level, data=request.data, partial=True)
    if serializer.is_valid():
        updated = serializer.save()
        return Response(
            {
                'message': 'Grade level updated successfully.',
                'grade_level': GradeLevelSerializer(updated).data
            }
        )
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_grade_level(request, grade_level_id):
    """
    Delete a grade level. Admin only.
    """
    if not is_admin(request):
        return Response({'error': 'Admin access required.'}, status=status.HTTP_403_FORBIDDEN)

    try:
        grade_level = GradeLevel.objects.get(grade_level_id=grade_level_id)
    except GradeLevel.DoesNotExist:
        return Response({'error': 'Grade level not found.'}, status=status.HTTP_404_NOT_FOUND)

    grade_level.delete()
    return Response({'message': 'Grade level deleted successfully.'}, status=status.HTTP_200_OK)
