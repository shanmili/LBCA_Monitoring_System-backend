from django.urls import path
from . import views

urlpatterns = [
    # Authentication
    path('api/parent/login/', views.parent_login, name='parent-login'),
    path('api/v1/parent/login/', views.parent_login, name='v1-parent-login'),
    path('api/parent/logout/', views.parent_logout, name='parent-logout'),
    path('api/v1/parent/logout/', views.parent_logout, name='v1-parent-logout'),
    
    # Profile Management
    path('api/parent/profile/', views.get_parent_profile, name='parent-profile'),
    path('api/v1/parent/profile/', views.get_parent_profile, name='v1-parent-profile'),
    path('api/parent/student-info/', views.get_student_info, name='student-info'),
    path('api/v1/parent/student-info/', views.get_student_info, name='v1-student-info'),
]
