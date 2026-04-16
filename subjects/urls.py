from django.urls import path
from . import views

urlpatterns = [
    path('api/subjects/', views.subjects_list_create, name='subjects-list-create'),
    path('api/v1/subjects/', views.subjects_list_create, name='v1-subjects-list-create'),
    path('api/subjects/<int:subject_id>/', views.subject_detail, name='subject-detail'),
    path('api/v1/subjects/<int:subject_id>/', views.subject_detail, name='v1-subject-detail'),
]
