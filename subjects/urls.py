from django.urls import path
from . import views

urlpatterns = [
    path('api/subjects/', views.list_subjects, name='list-subjects'),
    path('api/subjects/create/', views.create_subject, name='create-subject'),
    path('api/subjects/<int:subject_id>/', views.get_subject, name='get-subject'),
    path('api/subjects/<int:subject_id>/update/', views.update_subject, name='update-subject'),
    path('api/subjects/<int:subject_id>/delete/', views.delete_subject, name='delete-subject'),
]
