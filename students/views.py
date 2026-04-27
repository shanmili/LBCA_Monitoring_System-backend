from rest_framework import viewsets
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.decorators import action
from .models import Student, StudentEnrollment
from .serializers import StudentSerializer, StudentEnrollmentSerializer, StudentEnrollmentWithStudentSerializer


def is_admin(request):
    return (
        hasattr(request.user, 'teacher_profile')
        and request.user.teacher_profile.role == 'Admin'
    )

class StudentViewSet(viewsets.ModelViewSet):
    queryset = Student.objects.all()
    serializer_class = StudentSerializer
    permission_classes = [IsAuthenticated]

    def list(self, request, *args, **kwargs):
        students = Student.objects.all()
        serializer = self.get_serializer(students, many=True)
        return Response(serializer.data)

    def retrieve(self, request, *args, **kwargs):
        student_id = kwargs.get('pk')
        try:
            student = Student.objects.get(pk=student_id)
        except Student.DoesNotExist:
            return Response({'error': 'Student not found.'}, status=status.HTTP_404_NOT_FOUND)

        serializer = self.get_serializer(student)
        return Response(serializer.data)

    def create(self, request, *args, **kwargs):
        if not is_admin(request):
            return Response({'error': 'Admin access required.'}, status=status.HTTP_403_FORBIDDEN)

        serializer = self.get_serializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        student = serializer.save()

        return Response(
            {
                'message': 'Student created successfully.',
                'student_login_id': student.user.username,
                'student_login_password': student.user.username,
                'student': self.get_serializer(student).data,
            },
            status=status.HTTP_201_CREATED,
        )

    def update(self, request, *args, **kwargs):
        if not is_admin(request):
            return Response({'error': 'Admin access required.'}, status=status.HTTP_403_FORBIDDEN)

        student_id = kwargs.get('pk')
        try:
            student = Student.objects.get(pk=student_id)
        except Student.DoesNotExist:
            return Response({'error': 'Student not found.'}, status=status.HTTP_404_NOT_FOUND)

        serializer = self.get_serializer(student, data=request.data, partial=False)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({'message': 'Student updated successfully.', 'student': serializer.data})

    def partial_update(self, request, *args, **kwargs):
        if not is_admin(request):
            return Response({'error': 'Admin access required.'}, status=status.HTTP_403_FORBIDDEN)

        student_id = kwargs.get('pk')
        try:
            student = Student.objects.get(pk=student_id)
        except Student.DoesNotExist:
            return Response({'error': 'Student not found.'}, status=status.HTTP_404_NOT_FOUND)

        serializer = self.get_serializer(student, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({'message': 'Student updated successfully.', 'student': serializer.data})

    def destroy(self, request, *args, **kwargs):
        if not is_admin(request):
            return Response({'error': 'Admin access required.'}, status=status.HTTP_403_FORBIDDEN)

        student_id = kwargs.get('pk')
        try:
            student = Student.objects.get(pk=student_id)
        except Student.DoesNotExist:
            return Response({'error': 'Student not found.'}, status=status.HTTP_404_NOT_FOUND)

        student.delete()
        return Response({'message': 'Student deleted successfully.'})

class StudentEnrollmentViewSet(viewsets.ModelViewSet):
    queryset = StudentEnrollment.objects.all()
    serializer_class = StudentEnrollmentSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = StudentEnrollment.objects.all().order_by('id')
        student_id = self.request.query_params.get('student_id')
        school_year_id = self.request.query_params.get('school_year_id')

        if student_id:
            queryset = queryset.filter(student__id=student_id)
        if school_year_id:
            queryset = queryset.filter(school_year__school_year_id=school_year_id)

        return queryset

    def create(self, request, *args, **kwargs):
        if not is_admin(request):
            return Response({'error': 'Admin access required.'}, status=status.HTTP_403_FORBIDDEN)

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        enrollment = serializer.save(enrolled_by=request.user)

        return Response(
            {
                'message': 'Enrollment created successfully.',
                'enrollment': self.get_serializer(enrollment).data,
            },
            status=status.HTTP_201_CREATED,
        )

    def retrieve(self, request, *args, **kwargs):
        enrollment_id = kwargs.get('pk')
        try:
            enrollment = StudentEnrollment.objects.get(pk=enrollment_id)
        except StudentEnrollment.DoesNotExist:
            return Response({'error': 'Enrollment not found.'}, status=status.HTTP_404_NOT_FOUND)

        serializer = self.get_serializer(enrollment)
        return Response(serializer.data)

    def update(self, request, *args, **kwargs):
        if not is_admin(request):
            return Response({'error': 'Admin access required.'}, status=status.HTTP_403_FORBIDDEN)

        enrollment_id = kwargs.get('pk')
        try:
            enrollment = StudentEnrollment.objects.get(pk=enrollment_id)
        except StudentEnrollment.DoesNotExist:
            return Response({'error': 'Enrollment not found.'}, status=status.HTTP_404_NOT_FOUND)

        serializer = self.get_serializer(enrollment, data=request.data, partial=False)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({'message': 'Enrollment updated successfully.', 'enrollment': serializer.data})

    def partial_update(self, request, *args, **kwargs):
        if not is_admin(request):
            return Response({'error': 'Admin access required.'}, status=status.HTTP_403_FORBIDDEN)

        enrollment_id = kwargs.get('pk')
        try:
            enrollment = StudentEnrollment.objects.get(pk=enrollment_id)
        except StudentEnrollment.DoesNotExist:
            return Response({'error': 'Enrollment not found.'}, status=status.HTTP_404_NOT_FOUND)

        serializer = self.get_serializer(enrollment, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({'message': 'Enrollment updated successfully.', 'enrollment': serializer.data})

    def destroy(self, request, *args, **kwargs):
        if not is_admin(request):
            return Response({'error': 'Admin access required.'}, status=status.HTTP_403_FORBIDDEN)

        enrollment_id = kwargs.get('pk')
        try:
            enrollment = StudentEnrollment.objects.get(pk=enrollment_id)
        except StudentEnrollment.DoesNotExist:
            return Response({'error': 'Enrollment not found.'}, status=status.HTTP_404_NOT_FOUND)

        enrollment.delete()
        return Response({'message': 'Enrollment deleted successfully.'})

    @action(detail=False, methods=['post'], url_path='with-student')
    def create_with_student(self, request):
        if not is_admin(request):
            return Response({'error': 'Admin access required.'}, status=status.HTTP_403_FORBIDDEN)

        serializer = StudentEnrollmentWithStudentSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        result = serializer.save()

        return Response(
            {
                'message': 'Student and enrollment created successfully.',
                'student_login_id': result['student'].user.username,
                'student_login_password': result['student'].user.username,
                'student': StudentSerializer(result['student']).data,
                'enrollment': self.get_serializer(result['enrollment']).data,
            },
            status=status.HTTP_201_CREATED,
        )

    @action(detail=False, methods=['get'], url_path='by-student/(?P<student_id>[^/.]+)')
    def list_by_student(self, request, student_id=None):
        enrollments = self.get_queryset().filter(student__id=student_id)
        serializer = self.get_serializer(enrollments, many=True)
        return Response(serializer.data)