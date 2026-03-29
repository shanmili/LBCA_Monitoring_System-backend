from django.urls import path
from . import views

urlpatterns = [
    # List & Create
    path('api/sections/', views.list_sections, name='list-sections'),
    path('api/sections/create/', views.create_section, name='create-section'),

    # Filter by grade level (dedicated route)
    path('api/sections/grade-level/<int:grade_level_id>/', views.list_sections_by_grade_level, name='sections-by-grade-level'),

    # Single section operations
    path('api/sections/<int:section_id>/', views.get_section, name='get-section'),
    path('api/sections/<int:section_id>/update/', views.update_section, name='update-section'),
    path('api/sections/<int:section_id>/delete/', views.delete_section, name='delete-section'),
]
