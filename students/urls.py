from django.urls import path
from . import views

urlpatterns = [
    # Authentication
    path('login/', views.login, name='student-login'),
    
    # Students endpoints
    path('students/', views.list_students, name='list-students'),
    path('students/create/', views.create_student, name='create-student'),
    path('students/<int:student_id>/', views.get_student, name='get-student'),
    path('students/<int:student_id>/update/', views.update_student, name='update-student'),
    path('students/<int:student_id>/delete/', views.delete_student, name='delete-student'),
    
    # Enrollments endpoints
    path('enrollments/', views.list_enrollments, name='list-enrollments'),
    path('enrollments/create/', views.create_enrollment, name='create-enrollment'),
    path('enrollments/<int:enrollment_id>/', views.get_enrollment, name='get-enrollment'),
    path('enrollments/<int:enrollment_id>/update/', views.update_enrollment, name='update-enrollment'),
    path('enrollments/<int:enrollment_id>/delete/', views.delete_enrollment, name='delete-enrollment'),
]