from django.urls import path
from . import views

urlpatterns = [
    # Admin Registration
    path('api/admin/register/', views.admin_register, name='admin-register'),
    
    # Authentication
    path('api/teacher/login/', views.teacher_login, name='teacher-login'),
    path('api/teacher/logout/', views.teacher_logout, name='teacher-logout'),
    
    # Profile Management
    path('api/teacher/profile/', views.get_teacher_profile, name='teacher-profile'),
    path('api/teacher/profile/update/', views.update_teacher_profile, name='teacher-profile-update'),
    
    # Admin Only
    path('api/admin/teachers/create/', views.create_teacher, name='create-teacher'),
    path('api/admin/teachers/', views.list_teachers, name='list-teachers'),
    path('api/admin/teachers/<int:teacher_id>/delete/', views.delete_teacher, name='delete-teacher'),
    path('api/admin/teachers/<int:teacher_id>/reactivate/', views.reactivate_teacher, name='reactivate-teacher'),

    # Teacher Assignments
    path('api/teacher-assignments/', views.list_teacher_assignments, name='list-teacher-assignments'),
    path('api/teacher-assignments/create/', views.create_teacher_assignment, name='create-teacher-assignment'),
    path('api/teacher-assignments/<int:assignment_id>/', views.get_teacher_assignment, name='get-teacher-assignment'),
    path('api/teacher-assignments/<int:assignment_id>/update/', views.update_teacher_assignment, name='update-teacher-assignment'),
    path('api/teacher-assignments/<int:assignment_id>/delete/', views.delete_teacher_assignment, name='delete-teacher-assignment'),
]