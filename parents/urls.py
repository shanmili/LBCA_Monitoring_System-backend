from django.urls import path
from . import views

urlpatterns = [
    # Authentication
    path('api/parent/login/', views.parent_login, name='parent-login'),
    path('api/parent/logout/', views.parent_logout, name='parent-logout'),
    
    # Profile Management
    path('api/parent/profile/', views.get_parent_profile, name='parent-profile'),
    path('api/parent/student-info/', views.get_student_info, name='student-info'),
]
