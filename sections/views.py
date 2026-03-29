from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .models import Section
from .serializers import SectionSerializer
from grade_levels.models import GradeLevel


def is_admin(request):
    return (
        hasattr(request.user, 'teacher_profile')
        and request.user.teacher_profile.role == 'Admin'
    )


# ==================== SECTIONS CRUD ====================

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_sections(request):
    """
    List all sections.
    Optionally filter by grade_level_id via query param: ?grade_level_id=1
    Accessible by Admin and Teacher.
    """
    sections = Section.objects.all()

    grade_level_id = request.query_params.get('grade_level_id')
    if grade_level_id:
        sections = sections.filter(grade_level__grade_level_id=grade_level_id)

    serializer = SectionSerializer(sections, many=True)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_section(request, section_id):
    """
    Retrieve a single section by ID.
    """
    try:
        section = Section.objects.get(section_id=section_id)
        serializer = SectionSerializer(section)
        return Response(serializer.data)
    except Section.DoesNotExist:
        return Response({'error': 'Section not found.'}, status=status.HTTP_404_NOT_FOUND)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_sections_by_grade_level(request, grade_level_id):
    """
    List all sections under a specific grade level.
    """
    if not GradeLevel.objects.filter(grade_level_id=grade_level_id).exists():
        return Response({'error': 'Grade level not found.'}, status=status.HTTP_404_NOT_FOUND)

    sections = Section.objects.filter(grade_level__grade_level_id=grade_level_id)
    serializer = SectionSerializer(sections, many=True)
    return Response(serializer.data)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_section(request):
    """
    Create a new section. Admin only.
    Requires: grade_level (id), section_code, name
    """
    if not is_admin(request):
        return Response({'error': 'Admin access required.'}, status=status.HTTP_403_FORBIDDEN)

    serializer = SectionSerializer(data=request.data)
    if serializer.is_valid():
        section = serializer.save()
        return Response(
            {
                'message': 'Section created successfully.',
                'section': SectionSerializer(section).data
            },
            status=status.HTTP_201_CREATED
        )
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['PUT', 'PATCH'])
@permission_classes([IsAuthenticated])
def update_section(request, section_id):
    """
    Update a section. Admin only.
    """
    if not is_admin(request):
        return Response({'error': 'Admin access required.'}, status=status.HTTP_403_FORBIDDEN)

    try:
        section = Section.objects.get(section_id=section_id)
    except Section.DoesNotExist:
        return Response({'error': 'Section not found.'}, status=status.HTTP_404_NOT_FOUND)

    serializer = SectionSerializer(section, data=request.data, partial=True)
    if serializer.is_valid():
        updated = serializer.save()
        return Response(
            {
                'message': 'Section updated successfully.',
                'section': SectionSerializer(updated).data
            }
        )
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_section(request, section_id):
    """
    Delete a section. Admin only.
    """
    if not is_admin(request):
        return Response({'error': 'Admin access required.'}, status=status.HTTP_403_FORBIDDEN)

    try:
        section = Section.objects.get(section_id=section_id)
    except Section.DoesNotExist:
        return Response({'error': 'Section not found.'}, status=status.HTTP_404_NOT_FOUND)

    section.delete()
    return Response({'message': 'Section deleted successfully.'}, status=status.HTTP_200_OK)
