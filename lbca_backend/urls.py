from django.contrib import admin
from django.urls import path, include
from django.views.generic.base import RedirectView
from rest_framework.authtoken.views import obtain_auth_token
from rest_framework.permissions import AllowAny
from rest_framework.schemas import get_schema_view
from .views import public_api_root

try:
    from drf_yasg.views import get_schema_view as get_swagger_schema_view
    from drf_yasg import openapi
except ImportError:  # Optional dependency for Swagger UI
    get_swagger_schema_view = None

openapi_schema_view = get_schema_view(
    title='LBCA Monitoring API',
    description='API schema for localhost testing and documentation.',
    version='1.0.0',
    public=True,
    permission_classes=[AllowAny],
)

if get_swagger_schema_view:
    swagger_schema_view = get_swagger_schema_view(
        openapi.Info(
            title='LBCA Monitoring API',
            default_version='v1',
            description='Swagger documentation for LBCA backend endpoints.',
        ),
        public=True,
        permission_classes=(AllowAny,),
    )

urlpatterns = [
    # Redirect site root to API base so visiting the app URL shows the API
    path('', RedirectView.as_view(url='/api/', permanent=False), name='root-redirect'),
    path('admin/', admin.site.urls),
    path('api/token/', obtain_auth_token, name='api-token'),
    # Mount API root: prefer Swagger UI when available, otherwise serve a simple public root
    
    # If drf_yasg (Swagger) is available, show Swagger UI at `/api/` for a friendly API UI.
    if get_swagger_schema_view:
        urlpatterns = [
            path('api/', swagger_schema_view.with_ui('swagger', cache_timeout=0), name='api-swagger'),
        ]
        # append the rest of our urlpatterns below by extending later
    else:
        urlpatterns = [
            path('api/', public_api_root, name='public-api-root'),
        ]

    # include v1 app routes after the API root mapping
    urlpatterns += [
        path('api/v1/', include('students.urls')),
    ]
    path('api/schema/', openapi_schema_view, name='openapi-schema'),
    path('', include('teachers.urls')),
    path('', include('parents.urls')),
    path('', include('school_years.urls')),
    path('', include('grade_levels.urls')),
    path('', include('sections.urls')),
    path('', include('subjects.urls')),
    path('', include('schedules.urls')),
    path('', include('student_pace.urls')),
    path('', include('data_quality_log.urls')),
    # include other API endpoints (non-root paths)
    # non-root API includes (other apps will be mounted below)
    path('', include('teachers.urls')),
    path('', include('parents.urls')),
    path('', include('school_years.urls')),
    path('', include('grade_levels.urls')),
    path('', include('sections.urls')),
    path('', include('subjects.urls')),
    path('', include('schedules.urls')),
    path('', include('student_pace.urls')),
    path('', include('data_quality_log.urls')),
    # keep students app included under /api/ already via urlpatterns += above
]

if get_swagger_schema_view:
    urlpatterns += [
        path('swagger/', swagger_schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
        path('swagger.json/', swagger_schema_view.without_ui(cache_timeout=0), name='schema-swagger-json'),
    ]