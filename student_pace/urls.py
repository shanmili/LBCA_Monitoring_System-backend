from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import StudentPaceViewSet, EarlyWarningViewSet, get_student_pace, get_student_warnings, get_critical_warnings

router = DefaultRouter()
router.register(r'student-paces', StudentPaceViewSet, basename='studentpace')
router.register(r'early-warnings', EarlyWarningViewSet, basename='earlywarning')

urlpatterns = [
    # ViewSet routes (REST endpoints)
    path('api/', include(router.urls)),
    path('api/v1/', include(router.urls)),
    
    # Convenience endpoints for student-specific data
    path('api/student/<int:student_id>/pace/', get_student_pace, name='get-student-pace'),
    path('api/v1/student/<int:student_id>/pace/', get_student_pace, name='v1-get-student-pace'),
    path('api/student/<int:student_id>/warnings/', get_student_warnings, name='get-student-warnings'),
    path('api/v1/student/<int:student_id>/warnings/', get_student_warnings, name='v1-get-student-warnings'),
    path('api/critical-warnings/', get_critical_warnings, name='get-critical-warnings'),
    path('api/v1/critical-warnings/', get_critical_warnings, name='v1-get-critical-warnings'),
]
