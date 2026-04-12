from rest_framework import viewsets, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from .models import StudentPace, EarlyWarning
from .serializers import StudentPaceSerializer, EarlyWarningSerializer


class StudentPaceViewSet(viewsets.ModelViewSet):
    """
    API endpoint for student pace management
    GET: List all student paces
    POST: Create new student pace
    PUT/PATCH: Update student pace
    DELETE: Delete student pace
    """
    queryset = StudentPace.objects.all()
    serializer_class = StudentPaceSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Filter by student or enrollment if query parameters provided"""
        queryset = StudentPace.objects.all()
        student_id = self.request.query_params.get('student_id')
        enrollment_id = self.request.query_params.get('enrollment_id')
        
        if student_id:
            queryset = queryset.filter(student__id=student_id)
        if enrollment_id:
            queryset = queryset.filter(enrollment__id=enrollment_id)
        
        return queryset


class EarlyWarningViewSet(viewsets.ModelViewSet):
    """
    API endpoint for early warning management
    GET: List all early warnings
    POST: Create new early warning
    PUT/PATCH: Update early warning
    DELETE: Delete early warning
    """
    queryset = EarlyWarning.objects.all()
    serializer_class = EarlyWarningSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Filter by student, enrollment, or risk_level if query parameters provided"""
        queryset = EarlyWarning.objects.all()
        student_id = self.request.query_params.get('student_id')
        enrollment_id = self.request.query_params.get('enrollment_id')
        risk_level = self.request.query_params.get('risk_level')
        
        if student_id:
            queryset = queryset.filter(student__id=student_id)
        if enrollment_id:
            queryset = queryset.filter(enrollment__id=enrollment_id)
        if risk_level:
            queryset = queryset.filter(risk_level=risk_level)
        
        return queryset


# ==================== CONVENIENCE ENDPOINTS ====================

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_student_pace(request, student_id):
    """
    Get pace info for a specific student
    """
    paces = StudentPace.objects.filter(student__id=student_id)
    if not paces.exists():
        return Response({'error': 'No pace records found for this student'}, status=status.HTTP_404_NOT_FOUND)
    
    serializer = StudentPaceSerializer(paces, many=True)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_student_warnings(request, student_id):
    """
    Get all early warnings for a specific student
    """
    warnings = EarlyWarning.objects.filter(student__id=student_id)
    if not warnings.exists():
        return Response({'message': 'No warnings for this student'}, status=status.HTTP_200_OK)
    
    serializer = EarlyWarningSerializer(warnings, many=True)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_critical_warnings(request):
    """
    Get all critical early warnings (admin view)
    """
    warnings = EarlyWarning.objects.filter(risk_level='critical').order_by('-created_at')
    serializer = EarlyWarningSerializer(warnings, many=True)
    return Response(serializer.data)

