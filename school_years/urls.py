from django.urls import path
from . import views

urlpatterns = [
    # List & Create
    path('api/school-years/', views.school_years_list_create, name='school-years-list-create'),
    path('api/v1/school-years/', views.school_years_list_create, name='v1-school-years-list-create'),

    # Current active school year (custom action)
    path('api/school-years/current/', views.current_school_year, name='current-school-year'),
    path('api/v1/school-years/current/', views.current_school_year, name='v1-current-school-year'),

    # Single school year operations (GET, PUT, PATCH, DELETE)
    path('api/school-years/<int:school_year_id>/', views.school_year_detail, name='school-year-detail'),
    path('api/v1/school-years/<int:school_year_id>/', views.school_year_detail, name='v1-school-year-detail'),
]
