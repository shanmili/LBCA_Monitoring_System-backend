from django.urls import path
from . import views

urlpatterns = [
    path('api/schedules/', views.schedules_list_create, name='schedules-list-create'),
    path('api/schedules/<int:schedule_id>/', views.schedule_detail, name='schedule-detail'),
]
