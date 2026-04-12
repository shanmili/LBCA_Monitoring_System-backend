from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import StudentPaceViewSet, EarlyWarningViewSet, get_student_pace, get_student_warnings, get_critical_warnings

router = DefaultRouter()
router.register(r'student-paces', StudentPaceViewSet, basename='studentpace')
router.register(r'early-warnings', EarlyWarningViewSet, basename='earlywarning')

urlpatterns = [
    path('', include(router.urls)),
    
    # Convenience endpoints
    path('api/student/<int:student_id>/pace/', get_student_pace, name='get-student-pace'),
    path('api/student/<int:student_id>/warnings/', get_student_warnings, name='get-student-warnings'),
    path('api/critical-warnings/', get_critical_warnings, name='get-critical-warnings'),
]
