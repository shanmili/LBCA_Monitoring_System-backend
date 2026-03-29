from django.urls import path
from . import views

urlpatterns = [
    # List & Create
    path('api/school-years/', views.list_school_years, name='list-school-years'),
    path('api/school-years/create/', views.create_school_year, name='create-school-year'),

    # Current active school year
    path('api/school-years/current/', views.get_current_school_year, name='current-school-year'),

    # Single school year operations
    path('api/school-years/<int:school_year_id>/', views.get_school_year, name='get-school-year'),
    path('api/school-years/<int:school_year_id>/update/', views.update_school_year, name='update-school-year'),
    path('api/school-years/<int:school_year_id>/delete/', views.delete_school_year, name='delete-school-year'),
]
