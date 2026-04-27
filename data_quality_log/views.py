from rest_framework import status, viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied
from .models import DataQualityLog
from .serializers import DataQualityLogSerializer


class DataQualityLogViewSet(viewsets.ModelViewSet):
	queryset = DataQualityLog.objects.all()
	serializer_class = DataQualityLogSerializer
	permission_classes = [IsAuthenticated]
	lookup_field = 'log_id'

	def check_admin_permission(self):
		if not hasattr(self.request.user, 'teacher_profile') or self.request.user.teacher_profile.role != 'Admin':
			raise PermissionDenied('Admin access required')

	def create(self, request, *args, **kwargs):
		self.check_admin_permission()
		response = super().create(request, *args, **kwargs)
		return Response(
			{
				'message': 'Data quality log created successfully.',
				'log': response.data,
			},
			status=status.HTTP_201_CREATED,
		)

	def update(self, request, *args, **kwargs):
		self.check_admin_permission()
		response = super().update(request, *args, **kwargs)
		return Response(
			{
				'message': 'Data quality log updated successfully.',
				'log': response.data,
			},
			status=status.HTTP_200_OK,
		)

	def partial_update(self, request, *args, **kwargs):
		self.check_admin_permission()
		response = super().partial_update(request, *args, **kwargs)
		return Response(
			{
				'message': 'Data quality log updated successfully.',
				'log': response.data,
			},
			status=status.HTTP_200_OK,
		)

	def destroy(self, request, *args, **kwargs):
		self.check_admin_permission()
		self.get_object()
		super().destroy(request, *args, **kwargs)
		return Response({'message': 'Data quality log deleted successfully.'}, status=status.HTTP_200_OK)
