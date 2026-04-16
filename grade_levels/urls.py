from django.urls import path
from . import views

urlpatterns = [
    # List & Create
    path('api/grade-levels/', views.grade_levels_list_create, name='grade-levels-list-create'),
    path('api/v1/grade-levels/', views.grade_levels_list_create, name='v1-grade-levels-list-create'),

    # Single grade level operations (GET, PUT, PATCH, DELETE)
    path('api/grade-levels/<int:grade_level_id>/', views.grade_level_detail, name='grade-level-detail'),
    path('api/v1/grade-levels/<int:grade_level_id>/', views.grade_level_detail, name='v1-grade-level-detail'),
]
