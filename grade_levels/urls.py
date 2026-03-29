from django.urls import path
from . import views

urlpatterns = [
    # List & Create
    path('api/grade-levels/', views.list_grade_levels, name='list-grade-levels'),
    path('api/grade-levels/create/', views.create_grade_level, name='create-grade-level'),

    # Single grade level operations
    path('api/grade-levels/<int:grade_level_id>/', views.get_grade_level, name='get-grade-level'),
    path('api/grade-levels/<int:grade_level_id>/update/', views.update_grade_level, name='update-grade-level'),
    path('api/grade-levels/<int:grade_level_id>/delete/', views.delete_grade_level, name='delete-grade-level'),
]
