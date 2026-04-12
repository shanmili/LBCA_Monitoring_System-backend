from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('teachers.urls')),
    path('', include('parents.urls')),
    path('', include('school_years.urls')),
    path('', include('grade_levels.urls')),
    path('', include('sections.urls')),
    path('', include('subjects.urls')),
    path('', include('schedules.urls')),
    path('', include('student_pace.urls')),
    path('api/', include('students.urls')),
]