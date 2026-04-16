from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from drf_yasg.utils import swagger_auto_schema
from .models import Subject
from .serializers import SubjectSerializer


def is_admin(request):
    return (
        hasattr(request.user, 'teacher_profile')
        and request.user.teacher_profile.role == 'Admin'
    )


@swagger_auto_schema(
    method='get', responses={200: SubjectSerializer(many=True)},
    operation_description='List all subjects, optionally filter by grade_level_id'
)
@swagger_auto_schema(
    method='post', request_body=SubjectSerializer, responses={201: SubjectSerializer},
    operation_description='Create a new subject (Admin only)'
)
@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def subjects_list_create(request):
    """
    GET: List all subjects (optionally filter by ?grade_level_id=1)
    POST: Create a new subject (Admin only)
    """
    if request.method == 'GET':
        subjects = Subject.objects.all()
        grade_level_id = request.query_params.get('grade_level_id')
        if grade_level_id:
            subjects = subjects.filter(grade_level__grade_level_id=grade_level_id)
        
        serializer = SubjectSerializer(subjects, many=True)
        return Response(serializer.data)
    
    elif request.method == 'POST':
        if not is_admin(request):
            return Response({'error': 'Admin access required.'}, status=status.HTTP_403_FORBIDDEN)
        
        serializer = SubjectSerializer(data=request.data)
        if serializer.is_valid():
            subject = serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@swagger_auto_schema(
    method='get', responses={200: SubjectSerializer},
    operation_description='Retrieve a single subject by ID'
)
@swagger_auto_schema(
    method='put', request_body=SubjectSerializer, responses={200: SubjectSerializer},
    operation_description='Update a subject (Admin only)'
)
@swagger_auto_schema(
    method='patch', request_body=SubjectSerializer, responses={200: SubjectSerializer},
    operation_description='Partially update a subject (Admin only)'
)
@swagger_auto_schema(
    method='delete', responses={204: 'No content'},
    operation_description='Delete a subject (Admin only)'
)
@api_view(['GET', 'PUT', 'PATCH', 'DELETE'])
@permission_classes([IsAuthenticated])
def subject_detail(request, subject_id):
    """
    GET: Retrieve a single subject
    PUT: Update a subject (Admin only)
    PATCH: Partially update a subject (Admin only)
    DELETE: Delete a subject (Admin only)
    """
    try:
        subject = Subject.objects.get(subject_id=subject_id)
    except Subject.DoesNotExist:
        return Response({'error': 'Subject not found.'}, status=status.HTTP_404_NOT_FOUND)
    
    if request.method == 'GET':
        serializer = SubjectSerializer(subject)
        return Response(serializer.data)
    
    elif request.method in ['PUT', 'PATCH']:
        if not is_admin(request):
            return Response({'error': 'Admin access required.'}, status=status.HTTP_403_FORBIDDEN)
        
        serializer = SubjectSerializer(subject, data=request.data, partial=(request.method == 'PATCH'))
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    elif request.method == 'DELETE':
        if not is_admin(request):
            return Response({'error': 'Admin access required.'}, status=status.HTTP_403_FORBIDDEN)
        
        subject.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
