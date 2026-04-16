from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from drf_yasg.utils import swagger_auto_schema
from .models import ClassSchedule
from .serializers import ClassScheduleSerializer


def is_admin(request):
    return (
        hasattr(request.user, 'teacher_profile')
        and request.user.teacher_profile.role == 'Admin'
    )


@swagger_auto_schema(
    method='get', responses={200: ClassScheduleSerializer(many=True)},
    operation_description='List all schedules, optionally filter by section_id and/or day'
)
@swagger_auto_schema(
    method='post', request_body=ClassScheduleSerializer, responses={201: ClassScheduleSerializer},
    operation_description='Create a new schedule (Admin only)'
)
@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def schedules_list_create(request):
    """
    GET: List all schedules (optionally filter by ?section_id=1&day=Monday)
    POST: Create a new schedule (Admin only)
    """
    if request.method == 'GET':
        schedules = ClassSchedule.objects.all()
        
        section_id = request.query_params.get('section_id')
        day = request.query_params.get('day')
        
        if section_id:
            schedules = schedules.filter(section__section_id=section_id)
        if day:
            schedules = schedules.filter(day=day)
        
        serializer = ClassScheduleSerializer(schedules, many=True)
        return Response(serializer.data)
    
    elif request.method == 'POST':
        if not is_admin(request):
            return Response({'error': 'Admin access required.'}, status=status.HTTP_403_FORBIDDEN)
        
        serializer = ClassScheduleSerializer(data=request.data)
        if serializer.is_valid():
            schedule = serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@swagger_auto_schema(
    method='get', responses={200: ClassScheduleSerializer},
    operation_description='Retrieve a single schedule by ID'
)
@swagger_auto_schema(
    method='put', request_body=ClassScheduleSerializer, responses={200: ClassScheduleSerializer},
    operation_description='Update a schedule (Admin only)'
)
@swagger_auto_schema(
    method='patch', request_body=ClassScheduleSerializer, responses={200: ClassScheduleSerializer},
    operation_description='Partially update a schedule (Admin only)'
)
@swagger_auto_schema(
    method='delete', responses={204: 'No content'},
    operation_description='Delete a schedule (Admin only)'
)
@api_view(['GET', 'PUT', 'PATCH', 'DELETE'])
@permission_classes([IsAuthenticated])
def schedule_detail(request, schedule_id):
    """
    GET: Retrieve a single schedule
    PUT: Update a schedule (Admin only)
    PATCH: Partially update a schedule (Admin only)
    DELETE: Delete a schedule (Admin only)
    """
    try:
        schedule = ClassSchedule.objects.get(schedule_id=schedule_id)
    except ClassSchedule.DoesNotExist:
        return Response({'error': 'Schedule not found.'}, status=status.HTTP_404_NOT_FOUND)
    
    if request.method == 'GET':
        serializer = ClassScheduleSerializer(schedule)
        return Response(serializer.data)
    
    elif request.method in ['PUT', 'PATCH']:
        if not is_admin(request):
            return Response({'error': 'Admin access required.'}, status=status.HTTP_403_FORBIDDEN)
        
        serializer = ClassScheduleSerializer(schedule, data=request.data, partial=(request.method == 'PATCH'))
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    elif request.method == 'DELETE':
        if not is_admin(request):
            return Response({'error': 'Admin access required.'}, status=status.HTTP_403_FORBIDDEN)
        
        schedule.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
