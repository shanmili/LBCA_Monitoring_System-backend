from django.urls import path
from . import views

urlpatterns = [
    # Authentication
    path('api/login/', views.login, name='student-login'),
    
    # Students endpoints - specific paths first
    path('api/students/create/', views.create_student, name='create-student'),
    path('api/students/', views.list_students, name='list-students'),
    path('api/students/<int:student_id>/update/', views.update_student, name='update-student'),
    path('api/students/<int:student_id>/delete/', views.delete_student, name='delete-student'),
    path('api/students/<int:student_id>/', views.get_student, name='get-student'),
    
    # Enrollments endpoints - specific paths first
    path('api/students/enrollments/create/', views.create_enrollment, name='create-enrollment'),
    path('api/students/enrollments/', views.list_enrollments, name='list-enrollments'),
    path('api/students/enrollments/<int:enrollment_id>/update/', views.update_enrollment, name='update-enrollment'),
    path('api/students/enrollments/<int:enrollment_id>/delete/', views.delete_enrollment, name='delete-enrollment'),
    path('api/students/enrollments/<int:enrollment_id>/', views.get_enrollment, name='get-enrollment'),
]