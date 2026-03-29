from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .models import Subject
from .serializers import SubjectSerializer


def is_admin(request):
    return (
        hasattr(request.user, 'teacher_profile')
        and request.user.teacher_profile.role == 'Admin'
    )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_subjects(request):
    subjects = Subject.objects.all()

    grade_level_id = request.query_params.get('grade_level_id')
    if grade_level_id:
        subjects = subjects.filter(grade_level__grade_level_id=grade_level_id)

    serializer = SubjectSerializer(subjects, many=True)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_subject(request, subject_id):
    try:
        subject = Subject.objects.get(subject_id=subject_id)
    except Subject.DoesNotExist:
        return Response({'error': 'Subject not found.'}, status=status.HTTP_404_NOT_FOUND)

    serializer = SubjectSerializer(subject)
    return Response(serializer.data)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_subject(request):
    if not is_admin(request):
        return Response({'error': 'Admin access required.'}, status=status.HTTP_403_FORBIDDEN)

    serializer = SubjectSerializer(data=request.data)
    if serializer.is_valid():
        subject = serializer.save()
        return Response(
            {
                'message': 'Subject created successfully.',
                'subject': SubjectSerializer(subject).data,
            },
            status=status.HTTP_201_CREATED,
        )
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['PUT', 'PATCH'])
@permission_classes([IsAuthenticated])
def update_subject(request, subject_id):
    if not is_admin(request):
        return Response({'error': 'Admin access required.'}, status=status.HTTP_403_FORBIDDEN)

    try:
        subject = Subject.objects.get(subject_id=subject_id)
    except Subject.DoesNotExist:
        return Response({'error': 'Subject not found.'}, status=status.HTTP_404_NOT_FOUND)

    serializer = SubjectSerializer(subject, data=request.data, partial=True)
    if serializer.is_valid():
        updated_subject = serializer.save()
        return Response(
            {
                'message': 'Subject updated successfully.',
                'subject': SubjectSerializer(updated_subject).data,
            }
        )
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_subject(request, subject_id):
    if not is_admin(request):
        return Response({'error': 'Admin access required.'}, status=status.HTTP_403_FORBIDDEN)

    try:
        subject = Subject.objects.get(subject_id=subject_id)
    except Subject.DoesNotExist:
        return Response({'error': 'Subject not found.'}, status=status.HTTP_404_NOT_FOUND)

    subject.delete()
    return Response({'message': 'Subject deleted successfully.'}, status=status.HTTP_200_OK)
