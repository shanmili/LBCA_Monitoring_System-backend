from django.urls import path
from . import views

urlpatterns = [
    # List & Create
    path('api/sections/', views.sections_list_create, name='sections-list-create'),
    path('api/v1/sections/', views.sections_list_create, name='v1-sections-list-create'),

    # Filter by grade level (custom action)
    path('api/sections/grade-level/<int:grade_level_id>/', views.sections_by_grade_level, name='sections-by-grade-level'),
    path('api/v1/sections/grade-level/<int:grade_level_id>/', views.sections_by_grade_level, name='v1-sections-by-grade-level'),

    # Single section operations (GET, PUT, PATCH, DELETE)
    path('api/sections/<int:section_id>/', views.section_detail, name='section-detail'),
    path('api/v1/sections/<int:section_id>/', views.section_detail, name='v1-section-detail'),
]
