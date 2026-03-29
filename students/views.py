from rest_framework import viewsets
from rest_framework.permissions import AllowAny
from .models import Student, StudentEnrollment
from .serializers import StudentSerializer, StudentEnrollmentSerializer

class StudentViewSet(viewsets.ModelViewSet):
    queryset = Student.objects.all()
    serializer_class = StudentSerializer
    permission_classes = [AllowAny]

class StudentEnrollmentViewSet(viewsets.ModelViewSet):
    queryset = StudentEnrollment.objects.all()
    serializer_class = StudentEnrollmentSerializer
    permission_classes = [AllowAny]