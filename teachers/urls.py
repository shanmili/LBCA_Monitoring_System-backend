from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

# Configure routers for ViewSets
router = DefaultRouter()
router.register(r'', views.TeacherViewSet, basename='teacher')
router.register(r'assignments', views.TeacherAssignmentViewSet, basename='teacher-assignment')
router.register(r'availabilities', views.TeacherAvailabilityViewSet, basename='teacher-availability')

urlpatterns = [
    # ViewSet routes (REST endpoints)
    path('', include(router.urls)),
]