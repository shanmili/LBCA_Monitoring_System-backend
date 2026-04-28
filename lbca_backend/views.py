from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response


@api_view(['GET'])
@permission_classes([AllowAny])
def public_api_root(request):
    """Public API root that is accessible without authentication.

    This is safe to expose as it only provides links and does not reveal
    protected data. It helps browsers and the frontend discover API entry
    points without hitting the global IsAuthenticated default.
    """
    base = request.build_absolute_uri('/')[:-1]
    return Response({
        'api_root': f'{base}/api/',
        'admin_login': f'{base}/api/admin/login/',
        'teacher_login': f'{base}/api/teacher/login/',
        'swagger_ui': f'{base}/swagger/',
        'openapi_schema': f'{base}/api/schema/',
    })
