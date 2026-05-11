from django.contrib import admin
from django.urls import path, include
from django.views.generic.base import RedirectView
from rest_framework.authtoken.views import obtain_auth_token
from rest_framework.permissions import AllowAny
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView, SpectacularRedocView
from .views import public_api_root

urlpatterns = [
    # Redirect site root to API base
    path('', RedirectView.as_view(url='/api/', permanent=False), name='root-redirect'),
    path('admin/', admin.site.urls),
    path('api/token/', obtain_auth_token, name='api-token'),
    path('api/', public_api_root, name='public-api-root'),

    # Swagger UI routes
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),

    # App routes
    path('', include('students.urls')),
    path('', include('teachers.urls')),
    path('', include('parents.urls')),
    path('', include('school_years.urls')),
    path('', include('grade_levels.urls')),
    path('', include('sections.urls')),
    path('', include('subjects.urls')),
    path('', include('schedules.urls')),
    path('', include('student_pace.urls')),
    path('', include('data_quality_log.urls')),
]