from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('teachers.urls')),
    path('', include('school_years.urls')),
    path('', include('grade_levels.urls')),
    path('', include('sections.urls')),
]