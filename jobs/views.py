from rest_framework import generics, permissions
from .models import Job
from .serializers import JobSerializer
from accounts.permissions import IsEmployer
from .permissions import IsJobOwner


class JobListCreateView(generics.ListCreateAPIView):
    serializer_class = JobSerializer

    def get_permissions(self):
        if self.request.method == 'POST':
            return [permissions.IsAuthenticated(), IsEmployer()]
        return [permissions.AllowAny()]

    def get_queryset(self):
        return Job.objects.filter(status='open').select_related('employer')

    def perform_create(self, serializer):
        serializer.save(employer=self.request.user)


class JobRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = JobSerializer

    def get_permissions(self):
        if self.request.method == 'GET':
            return [permissions.AllowAny()]
        return [permissions.IsAuthenticated(), IsEmployer(), IsJobOwner()]

    def get_queryset(self):
        return Job.objects.select_related('employer')

    def partial_update(self, request, *args, **kwargs):
        kwargs['partial'] = True
        return self.update(request, *args, **kwargs)