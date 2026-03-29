from django.urls import path
from . import views

urlpatterns = [
    path('api/schedules/', views.list_schedules, name='list-schedules'),
    path('api/schedules/create/', views.create_schedule, name='create-schedule'),
    path('api/schedules/<int:schedule_id>/', views.get_schedule, name='get-schedule'),
    path('api/schedules/<int:schedule_id>/update/', views.update_schedule, name='update-schedule'),
    path('api/schedules/<int:schedule_id>/delete/', views.delete_schedule, name='delete-schedule'),
]
