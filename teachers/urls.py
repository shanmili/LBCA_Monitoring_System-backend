from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

# Configure routers for ViewSets
router = DefaultRouter()
router.register(r'teachers', views.TeacherViewSet, basename='teacher')
router.register(r'teacher-assignments', views.TeacherAssignmentViewSet, basename='teacher-assignment')
router.register(r'teacher-availabilities', views.TeacherAvailabilityViewSet, basename='teacher-availability')

urlpatterns = [
    # ViewSet routes (REST endpoints)
    path('api/', include(router.urls)),
    path('api/v1/', include(router.urls)),
    
    # Authentication endpoints (custom routes)
    path('api/admin/register/', views.admin_register, name='admin-register'),
    path('api/v1/admin/register/', views.admin_register, name='v1-admin-register'),
    
    path('api/admin/login/', views.admin_login, name='admin-login'),
    path('api/v1/admin/login/', views.admin_login, name='v1-admin-login'),
    
    path('api/teacher/login/', views.teacher_login, name='teacher-login'),
    path('api/v1/teacher/login/', views.teacher_login, name='v1-teacher-login'),
    
    path('api/teacher/logout/', views.teacher_logout, name='teacher-logout'),
    path('api/v1/teacher/logout/', views.teacher_logout, name='v1-teacher-logout'),
    
    # Profile endpoints (custom routes)
    path('api/teacher/profile/', views.get_teacher_profile, name='teacher-profile'),
    path('api/v1/teacher/profile/', views.get_teacher_profile, name='v1-teacher-profile'),
    
    path('api/teacher/profile/update/', views.update_teacher_profile, name='teacher-profile-update'),
    path('api/v1/teacher/profile/update/', views.update_teacher_profile, name='v1-teacher-profile-update'),
]