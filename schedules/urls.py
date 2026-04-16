from django.urls import path
from . import views

urlpatterns = [
    path('api/schedules/', views.schedules_list_create, name='schedules-list-create'),
    path('api/v1/schedules/', views.schedules_list_create, name='v1-schedules-list-create'),
    path('api/schedules/<int:schedule_id>/', views.schedule_detail, name='schedule-detail'),
    path('api/v1/schedules/<int:schedule_id>/', views.schedule_detail, name='v1-schedule-detail'),
]
