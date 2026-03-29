from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .models import SchoolYear
from .serializers import SchoolYearSerializer


def is_admin(request):
    return (
        hasattr(request.user, 'teacher_profile')
        and request.user.teacher_profile.role == 'Admin'
    )


# ==================== SCHOOL YEAR CRUD ====================

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_school_years(request):
    """
    List all school years.
    Accessible by Admin and Teacher.
    """
    school_years = SchoolYear.objects.all()
    serializer = SchoolYearSerializer(school_years, many=True)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_current_school_year(request):
    """
    Get the current active school year.
    """
    try:
        school_year = SchoolYear.objects.get(is_current=True)
        serializer = SchoolYearSerializer(school_year)
        return Response(serializer.data)
    except SchoolYear.DoesNotExist:
        return Response(
            {'error': 'No active school year found.'},
            status=status.HTTP_404_NOT_FOUND
        )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_school_year(request, school_year_id):
    """
    Retrieve a single school year by ID.
    """
    try:
        school_year = SchoolYear.objects.get(school_year_id=school_year_id)
        serializer = SchoolYearSerializer(school_year)
        return Response(serializer.data)
    except SchoolYear.DoesNotExist:
        return Response({'error': 'School year not found.'}, status=status.HTTP_404_NOT_FOUND)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_school_year(request):
    """
    Create a new school year. Admin only.
    If is_current=True, all other school years are set to is_current=False.
    """
    if not is_admin(request):
        return Response({'error': 'Admin access required.'}, status=status.HTTP_403_FORBIDDEN)

    serializer = SchoolYearSerializer(data=request.data)
    if serializer.is_valid():
        # If new school year is current, clear existing current
        if serializer.validated_data.get('is_current', False):
            SchoolYear.objects.filter(is_current=True).update(is_current=False)

        school_year = serializer.save()
        return Response(
            {
                'message': 'School year created successfully.',
                'school_year': SchoolYearSerializer(school_year).data
            },
            status=status.HTTP_201_CREATED
        )
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['PUT', 'PATCH'])
@permission_classes([IsAuthenticated])
def update_school_year(request, school_year_id):
    """
    Update a school year. Admin only.
    If is_current=True, all other school years are set to is_current=False.
    """
    if not is_admin(request):
        return Response({'error': 'Admin access required.'}, status=status.HTTP_403_FORBIDDEN)

    try:
        school_year = SchoolYear.objects.get(school_year_id=school_year_id)
    except SchoolYear.DoesNotExist:
        return Response({'error': 'School year not found.'}, status=status.HTTP_404_NOT_FOUND)

    serializer = SchoolYearSerializer(school_year, data=request.data, partial=True)
    if serializer.is_valid():
        if serializer.validated_data.get('is_current', False):
            SchoolYear.objects.exclude(school_year_id=school_year_id).update(is_current=False)

        updated = serializer.save()
        return Response(
            {
                'message': 'School year updated successfully.',
                'school_year': SchoolYearSerializer(updated).data
            }
        )
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_school_year(request, school_year_id):
    """
    Delete a school year. Admin only.
    Cannot delete the currently active school year.
    """
    if not is_admin(request):
        return Response({'error': 'Admin access required.'}, status=status.HTTP_403_FORBIDDEN)

    try:
        school_year = SchoolYear.objects.get(school_year_id=school_year_id)
    except SchoolYear.DoesNotExist:
        return Response({'error': 'School year not found.'}, status=status.HTTP_404_NOT_FOUND)

    if school_year.is_current:
        return Response(
            {'error': 'Cannot delete the currently active school year.'},
            status=status.HTTP_400_BAD_REQUEST
        )

    school_year.delete()
    return Response({'message': 'School year deleted successfully.'}, status=status.HTTP_200_OK)
