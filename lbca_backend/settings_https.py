from .settings import *

# Override CORS and CSRF origins to HTTPS only
CORS_ALLOWED_ORIGINS = [
    "https://lbca-monitoring-system.onrender.com",
    'http://localhost:5173',
    'http://127.0.0.1:5173',
    'https://localhost:5173',
    'https://127.0.0.1:5173',
]

CSRF_TRUSTED_ORIGINS = [
    "https://lbca-monitoring-system.onrender.com",
    'http://localhost:5173',
    'http://127.0.0.1:5173',
    'https://localhost:5173',
    'https://127.0.0.1:5173',
]

# HTTPS security settings
SECURE_SSL_REDIRECT = True
SECURE_HSTS_SECONDS = 31536000
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True