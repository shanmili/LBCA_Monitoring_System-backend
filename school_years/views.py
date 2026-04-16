from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from drf_yasg.utils import swagger_auto_schema
from .models import SchoolYear
from .serializers import SchoolYearSerializer


def is_admin(request):
    return (
        hasattr(request.user, 'teacher_profile')
        and request.user.teacher_profile.role == 'Admin'
    )


# ==================== SCHOOL YEAR CRUD ====================

@swagger_auto_schema(
    method='get', responses={200: SchoolYearSerializer(many=True)},
    operation_description='List all school years'
)
@swagger_auto_schema(
    method='post', request_body=SchoolYearSerializer, responses={201: SchoolYearSerializer},
    operation_description='Create a new school year (Admin only)'
)
@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def school_years_list_create(request):
    """
    GET: List all school years
    POST: Create a new school year (Admin only)
    """
    if request.method == 'GET':
        school_years = SchoolYear.objects.all()
        serializer = SchoolYearSerializer(school_years, many=True)
        return Response(serializer.data)
    
    elif request.method == 'POST':
        if not is_admin(request):
            return Response({'error': 'Admin access required.'}, status=status.HTTP_403_FORBIDDEN)
        
        serializer = SchoolYearSerializer(data=request.data)
        if serializer.is_valid():
            if serializer.validated_data.get('is_current', False):
                SchoolYear.objects.filter(is_current=True).update(is_current=False)
            
            school_year = serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@swagger_auto_schema(
    method='get', responses={200: SchoolYearSerializer},
    operation_description='Get the current active school year'
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def current_school_year(request):
    """
    GET: Get the current active school year
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


@swagger_auto_schema(
    method='get', responses={200: SchoolYearSerializer},
    operation_description='Retrieve a single school year by ID'
)
@swagger_auto_schema(
    method='put', request_body=SchoolYearSerializer, responses={200: SchoolYearSerializer},
    operation_description='Update a school year (Admin only)'
)
@swagger_auto_schema(
    method='patch', request_body=SchoolYearSerializer, responses={200: SchoolYearSerializer},
    operation_description='Partially update a school year (Admin only)'
)
@swagger_auto_schema(
    method='delete', responses={204: 'No content'},
    operation_description='Delete a school year (Admin only)'
)
@api_view(['GET', 'PUT', 'PATCH', 'DELETE'])
@permission_classes([IsAuthenticated])
def school_year_detail(request, school_year_id):
    """
    GET: Retrieve a single school year
    PUT: Update a school year (Admin only)
    PATCH: Partially update a school year (Admin only)
    DELETE: Delete a school year (Admin only)
    """
    try:
        school_year = SchoolYear.objects.get(school_year_id=school_year_id)
    except SchoolYear.DoesNotExist:
        return Response({'error': 'School year not found.'}, status=status.HTTP_404_NOT_FOUND)
    
    if request.method == 'GET':
        serializer = SchoolYearSerializer(school_year)
        return Response(serializer.data)
    
    elif request.method in ['PUT', 'PATCH']:
        if not is_admin(request):
            return Response({'error': 'Admin access required.'}, status=status.HTTP_403_FORBIDDEN)
        
        serializer = SchoolYearSerializer(school_year, data=request.data, partial=(request.method == 'PATCH'))
        if serializer.is_valid():
            if serializer.validated_data.get('is_current', False):
                SchoolYear.objects.exclude(school_year_id=school_year_id).update(is_current=False)
            
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    elif request.method == 'DELETE':
        if not is_admin(request):
            return Response({'error': 'Admin access required.'}, status=status.HTTP_403_FORBIDDEN)
        
        if school_year.is_current:
            return Response(
                {'error': 'Cannot delete the currently active school year.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        school_year.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
