from rest_framework import viewsets
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
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

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)

        enrollment = serializer.instance
        student_user = enrollment.student.user

        response_data = dict(serializer.data)
        response_data['student_id'] = enrollment.student.id
        response_data['student_login_id'] = student_user.username
        response_data['student_login_password'] = student_user.username

        headers = self.get_success_headers(serializer.data)
        return Response(response_data, status=status.HTTP_201_CREATED, headers=headers)