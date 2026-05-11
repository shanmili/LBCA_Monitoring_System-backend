from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import StudentViewSet, StudentEnrollmentViewSet

router = DefaultRouter()
router.register(r'students', StudentViewSet)
router.register(r'enrollments', StudentEnrollmentViewSet)

urlpatterns = [
    # Support both /api/ and /api/v1/ paths
    path('api/', include(router.urls)),
    path('api/v1/', include(router.urls)),
    
    # Student enrollments by student ID
    path('api/students/<int:student_id>/enrollments/',
        StudentEnrollmentViewSet.as_view({'get': 'list_by_student'}),
        name='student-enrollments-by-student'),
    path('api/v1/students/<int:student_id>/enrollments/',
        StudentEnrollmentViewSet.as_view({'get': 'list_by_student'}),
        name='v1-student-enrollments-by-student'),
]