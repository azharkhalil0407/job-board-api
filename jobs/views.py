from rest_framework import generics, permissions, status
from rest_framework.exceptions import ValidationError
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from .models import Job, Application
from .serializers import JobSerializer, ApplicationSerializer, ApplicationStatusUpdateSerializer
from .filters import JobFilter
from accounts.permissions import IsEmployer, IsCandidate
from .permissions import IsJobOwner, IsApplicationJobOwner, IsApplicationOwner


#job views
class JobListCreateView(generics.ListCreateAPIView):
    serializer_class = JobSerializer
    filterset_class = JobFilter
    search_fields = ['title', 'description']
    ordering_fields = ['created_at', 'salary_min', 'salary_max']
    ordering = ['-created_at']

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


#application views
class JobApplyView(generics.CreateAPIView):
    serializer_class = ApplicationSerializer
    permission_classes = [permissions.IsAuthenticated, IsCandidate]
    parser_classes = [MultiPartParser, FormParser, JSONParser]

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


class ApplicationPagination(PageNumberPagination):
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100


class ApplicationListView(generics.ListAPIView):
    serializer_class = ApplicationSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = ApplicationPagination

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


class ResumeUploadView(generics.UpdateAPIView):
    serializer_class = ApplicationSerializer
    permission_classes = [permissions.IsAuthenticated, IsCandidate, IsApplicationOwner]
    parser_classes = [MultiPartParser, FormParser]
    http_method_names = ['patch']

    def get_queryset(self):
        return Application.objects.filter(
            candidate=self.request.user
        ).select_related('candidate', 'job')

    def patch(self, request, *args, **kwargs):
        application = self.get_object()
        file = request.FILES.get('resume')

        if not file:
            return Response(
                {"resume": "No file was submitted."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        serializer = self.get_serializer(
            application,
            data={'resume': file},
            partial=True,
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data, status=status.HTTP_200_OK)