"""
Initialization endpoint for Render deployment
Allows one-time setup of database when Render Shell is not available
"""
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
from django.core.management import call_command
from django.conf import settings
import os


@api_view(['POST'])
@permission_classes([AllowAny])
def init_database(request):
    """
    Initialize database with migrations and seed data
    
    POST body (optional):
    {
        "init_key": "your-secret-key-from-env"
    }
    
    Only works if INIT_SECRET_KEY is set in environment
    """
    
    # Check if initialization is allowed
    init_key_env = os.getenv('INIT_SECRET_KEY')
    
    if not init_key_env:
        return Response(
            {'error': 'Initialization is disabled (INIT_SECRET_KEY not set)'},
            status=status.HTTP_403_FORBIDDEN
        )
    
    # Validate provided key
    provided_key = request.data.get('init_key')
    if provided_key != init_key_env:
        return Response(
            {'error': 'Invalid or missing init_key'},
            status=status.HTTP_401_UNAUTHORIZED
        )
    
    try:
        # Run migrations
        call_command('migrate', verbosity=1)
        migration_result = "✓ Migrations completed"
    except Exception as e:
        migration_result = f"Migration error (may be normal if already run): {str(e)}"
    
    try:
        # Run seeder
        os.system('python django_seed_admin.py')
        seed_result = "✓ Seed data created"
    except Exception as e:
        seed_result = f"Seed error: {str(e)}"
    
    return Response({
        'status': 'Database initialization completed',
        'migrations': migration_result,
        'seed': seed_result,
        'next_steps': [
            'Test login at /api/teacher/login/ with ADMIN001:ADMIN001',
            'Access API docs at /api/docs/',
            'If you see this message, initialization is COMPLETE'
        ]
    }, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([AllowAny])
def init_status(request):
    """Check database initialization status"""
    from django.contrib.auth.models import User
    
    try:
        admin_count = User.objects.filter(username__startswith='ADMIN').count()
        return Response({
            'database': 'connected',
            'admin_accounts': admin_count,
            'status': 'ready' if admin_count > 0 else 'needs_initialization'
        })
    except Exception as e:
        return Response({
            'database': 'error',
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
