from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import StudentViewSet, StudentEnrollmentViewSet

router = DefaultRouter()
router.register(r'', StudentViewSet, basename='student')
router.register(r'enrollments', StudentEnrollmentViewSet, basename='enrollment')

urlpatterns = [
    # Main router (includes students/ and enrollments/)
    path('', include(router.urls)),
    
    # Student enrollments by student ID
    path('<int:student_id>/enrollments/',
        StudentEnrollmentViewSet.as_view({'get': 'list_by_student'}),
        name='student-enrollments-by-student'),
]