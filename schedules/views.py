from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .models import ClassSchedule
from .serializers import ClassScheduleSerializer


def is_admin(request):
    return (
        hasattr(request.user, 'teacher_profile')
        and request.user.teacher_profile.role == 'Admin'
    )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_schedules(request):
    schedules = ClassSchedule.objects.all()

    section_id = request.query_params.get('section_id')
    day = request.query_params.get('day')

    if section_id:
        schedules = schedules.filter(section__section_id=section_id)
    if day:
        schedules = schedules.filter(day=day)

    serializer = ClassScheduleSerializer(schedules, many=True)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_schedule(request, schedule_id):
    try:
        schedule = ClassSchedule.objects.get(schedule_id=schedule_id)
    except ClassSchedule.DoesNotExist:
        return Response({'error': 'Schedule not found.'}, status=status.HTTP_404_NOT_FOUND)

    serializer = ClassScheduleSerializer(schedule)
    return Response(serializer.data)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_schedule(request):
    if not is_admin(request):
        return Response({'error': 'Admin access required.'}, status=status.HTTP_403_FORBIDDEN)

    serializer = ClassScheduleSerializer(data=request.data)
    if serializer.is_valid():
        schedule = serializer.save()
        return Response(
            {
                'message': 'Schedule created successfully.',
                'schedule': ClassScheduleSerializer(schedule).data,
            },
            status=status.HTTP_201_CREATED,
        )
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['PUT', 'PATCH'])
@permission_classes([IsAuthenticated])
def update_schedule(request, schedule_id):
    if not is_admin(request):
        return Response({'error': 'Admin access required.'}, status=status.HTTP_403_FORBIDDEN)

    try:
        schedule = ClassSchedule.objects.get(schedule_id=schedule_id)
    except ClassSchedule.DoesNotExist:
        return Response({'error': 'Schedule not found.'}, status=status.HTTP_404_NOT_FOUND)

    serializer = ClassScheduleSerializer(schedule, data=request.data, partial=True)
    if serializer.is_valid():
        updated_schedule = serializer.save()
        return Response(
            {
                'message': 'Schedule updated successfully.',
                'schedule': ClassScheduleSerializer(updated_schedule).data,
            }
        )
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_schedule(request, schedule_id):
    if not is_admin(request):
        return Response({'error': 'Admin access required.'}, status=status.HTTP_403_FORBIDDEN)

    try:
        schedule = ClassSchedule.objects.get(schedule_id=schedule_id)
    except ClassSchedule.DoesNotExist:
        return Response({'error': 'Schedule not found.'}, status=status.HTTP_404_NOT_FOUND)

    schedule.delete()
    return Response({'message': 'Schedule deleted successfully.'}, status=status.HTTP_200_OK)
