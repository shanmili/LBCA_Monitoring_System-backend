from django.urls import path
from . import views

urlpatterns = [
    path('api/subjects/', views.subjects_list_create, name='subjects-list-create'),
    path('api/subjects/<int:subject_id>/', views.subject_detail, name='subject-detail'),
]
