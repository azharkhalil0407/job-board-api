from rest_framework import generics, permissions
from rest_framework.exceptions import PermissionDenied, ValidationError
from .models import Job, Application
from .serializers import JobSerializer, ApplicationSerializer, ApplicationStatusUpdateSerializer
from accounts.permissions import IsEmployer, IsCandidate
from .permissions import IsJobOwner, IsApplicationOwner, IsApplicationJobOwner


#JOB VIEWS
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


#APPLICATION VIEWS
class JobApplyView(generics.CreateAPIView):
    serializer_class = ApplicationSerializer
    permission_classes = [permissions.IsAuthenticated, IsCandidate]

    def get_queryset(self):
        return Application.objects.select_related('candidate', 'job')

    def perform_create(self, serializer):
        job_id = self.kwargs.get('pk')
        try:
            job = Job.objects.get(pk=job_id, status='open')
        except Job.DoesNotExist:
            raise ValidationError("Job does not exist or is no longer open.")

        if Application.objects.filter(job=job, candidate=self.request.user).exists():
            raise ValidationError("You have already applied to this job.")

        serializer.save(candidate=self.request.user, job=job)


class ApplicationListView(generics.ListAPIView):
    serializer_class = ApplicationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.role == 'employer':
            return Application.objects.filter(
                job__employer=user
            ).select_related('candidate', 'job', 'job__employer')
        return Application.objects.filter(
            candidate=user
        ).select_related('candidate', 'job', 'job__employer')


class ApplicationRetrieveView(generics.RetrieveAPIView):
    serializer_class = ApplicationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.role == 'employer':
            return Application.objects.filter(
                job__employer=user
            ).select_related('candidate', 'job')
        return Application.objects.filter(
            candidate=user
        ).select_related('candidate', 'job')


class ApplicationStatusUpdateView(generics.UpdateAPIView):
    serializer_class = ApplicationStatusUpdateSerializer
    permission_classes = [permissions.IsAuthenticated, IsEmployer, IsApplicationJobOwner]
    http_method_names = ['patch']

    def get_queryset(self):
        return Application.objects.select_related(
            'candidate', 'job', 'job__employer'
        )