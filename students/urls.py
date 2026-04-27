from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import StudentViewSet, StudentEnrollmentViewSet

router = DefaultRouter()
router.register(r'students', StudentViewSet)
router.register(r'enrollments', StudentEnrollmentViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path(
        'students/<int:student_id>/enrollments/',
        StudentEnrollmentViewSet.as_view({'get': 'list_by_student'}),
        name='student-enrollments-by-student',
    ),
]