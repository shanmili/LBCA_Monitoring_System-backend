from django.urls import include, path
from rest_framework.routers import DefaultRouter
from .views import DataQualityLogViewSet

router = DefaultRouter()
router.register(r'data-quality-logs', DataQualityLogViewSet, basename='data-quality-log')

urlpatterns = [
    path('api/', include(router.urls)),
]
