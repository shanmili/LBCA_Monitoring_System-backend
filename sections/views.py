from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from drf_yasg.utils import swagger_auto_schema
from .models import Section
from .serializers import SectionSerializer
from grade_levels.models import GradeLevel


def is_admin(request):
    return (
        hasattr(request.user, 'teacher_profile')
        and request.user.teacher_profile.role == 'Admin'
    )


# ==================== SECTIONS CRUD ====================

@swagger_auto_schema(
    method='get', responses={200: SectionSerializer(many=True)},
    operation_description='List all sections, optionally filter by grade_level_id'
)
@swagger_auto_schema(
    method='post', request_body=SectionSerializer, responses={201: SectionSerializer},
    operation_description='Create a new section (Admin only)'
)
@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def sections_list_create(request):
    """
    GET: List all sections (optionally filter by ?grade_level_id=1)
    POST: Create a new section (Admin only)
    """
    if request.method == 'GET':
        sections = Section.objects.all()
        grade_level_id = request.query_params.get('grade_level_id')
        if grade_level_id:
            sections = sections.filter(grade_level__grade_level_id=grade_level_id)
        
        serializer = SectionSerializer(sections, many=True)
        return Response(serializer.data)
    
    elif request.method == 'POST':
        if not is_admin(request):
            return Response({'error': 'Admin access required.'}, status=status.HTTP_403_FORBIDDEN)
        
        serializer = SectionSerializer(data=request.data)
        if serializer.is_valid():
            section = serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@swagger_auto_schema(
    method='get', responses={200: SectionSerializer(many=True)},
    operation_description='List all sections under a specific grade level'
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def sections_by_grade_level(request, grade_level_id):
    """
    GET: List all sections under a specific grade level
    """
    if not GradeLevel.objects.filter(grade_level_id=grade_level_id).exists():
        return Response({'error': 'Grade level not found.'}, status=status.HTTP_404_NOT_FOUND)

    sections = Section.objects.filter(grade_level__grade_level_id=grade_level_id)
    serializer = SectionSerializer(sections, many=True)
    return Response(serializer.data)


@swagger_auto_schema(
    method='get', responses={200: SectionSerializer},
    operation_description='Retrieve a single section by ID'
)
@swagger_auto_schema(
    method='put', request_body=SectionSerializer, responses={200: SectionSerializer},
    operation_description='Update a section (Admin only)'
)
@swagger_auto_schema(
    method='patch', request_body=SectionSerializer, responses={200: SectionSerializer},
    operation_description='Partially update a section (Admin only)'
)
@swagger_auto_schema(
    method='delete', responses={204: 'No content'},
    operation_description='Delete a section (Admin only)'
)
@api_view(['GET', 'PUT', 'PATCH', 'DELETE'])
@permission_classes([IsAuthenticated])
def section_detail(request, section_id):
    """
    GET: Retrieve a single section
    PUT: Update a section (Admin only)
    PATCH: Partially update a section (Admin only)
    DELETE: Delete a section (Admin only)
    """
    try:
        section = Section.objects.get(section_id=section_id)
    except Section.DoesNotExist:
        return Response({'error': 'Section not found.'}, status=status.HTTP_404_NOT_FOUND)
    
    if request.method == 'GET':
        serializer = SectionSerializer(section)
        return Response(serializer.data)
    
    elif request.method in ['PUT', 'PATCH']:
        if not is_admin(request):
            return Response({'error': 'Admin access required.'}, status=status.HTTP_403_FORBIDDEN)
        
        serializer = SectionSerializer(section, data=request.data, partial=(request.method == 'PATCH'))
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    elif request.method == 'DELETE':
        if not is_admin(request):
            return Response({'error': 'Admin access required.'}, status=status.HTTP_403_FORBIDDEN)
        
        section.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
