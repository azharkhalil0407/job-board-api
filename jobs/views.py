from rest_framework import generics, permissions
from rest_framework.exceptions import PermissionDenied
from .models import Job
from .serializers import JobSerializer


class JobListCreateView(generics.ListCreateAPIView):
    serializer_class = JobSerializer

    def get_permissions(self):
        if self.request.method == 'POST':
            return [permissions.IsAuthenticated()]
        return [permissions.AllowAny()]

    def get_queryset(self):
        return Job.objects.filter(status='open').select_related('employer')

    def perform_create(self, serializer):
        if self.request.user.role != 'employer':
            raise PermissionDenied("Only employers can post jobs.")
        serializer.save(employer=self.request.user)


class JobRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = JobSerializer

    def get_queryset(self):
        return Job.objects.select_related('employer')

    def get_permissions(self):
        if self.request.method == 'GET':
            return [permissions.AllowAny()]
        return [permissions.IsAuthenticated()]

    def perform_update(self, serializer):
        if self.request.user != self.get_object().employer:
            raise PermissionDenied("You can only edit your own job postings.")
        serializer.save()

    def perform_destroy(self, instance):
        if self.request.user != instance.employer:
            raise PermissionDenied("You can only delete your own job postings.")
        instance.delete()

    def partial_update(self, request, *args, **kwargs):
        kwargs['partial'] = True
        return self.update(request, *args, **kwargs)