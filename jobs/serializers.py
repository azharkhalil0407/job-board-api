from rest_framework import serializers
from .models import Job, Application
from accounts.serializers import UserSerializer


class JobSerializer(serializers.ModelSerializer):
    employer = UserSerializer(read_only=True)
    application_count = serializers.SerializerMethodField()

    class Meta:
        model = Job
        fields = [
            'id', 'employer', 'title', 'description', 'location',
            'salary_min', 'salary_max', 'status',
            'application_count', 'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def get_application_count(self, obj):
        return obj.applications.count()

    def validate(self, data):
        salary_min = data.get('salary_min')
        salary_max = data.get('salary_max')
        if salary_min and salary_max and salary_min > salary_max:
            raise serializers.ValidationError(
                "salary_min cannot be greater than salary_max."
            )
        return data


class ApplicationSerializer(serializers.ModelSerializer):
    candidate = UserSerializer(read_only=True)
    job_title = serializers.CharField(source='job.title', read_only=True)

    class Meta:
        model = Application
        fields = [
            'id', 'job', 'job_title', 'candidate', 'status',
            'cover_letter', 'resume', 'applied_at', 'updated_at',
        ]
        read_only_fields = ['id', 'job','applied_at', 'updated_at']


class ApplicationStatusUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Application
        fields = ['status']

    def validate_status(self, value):
        valid_transitions = {
            'applied': ['reviewed', 'rejected'],
            'reviewed': ['accepted', 'rejected'],
            'accepted': [],
            'rejected': [],
        }
        current_status = self.instance.status
        if value not in valid_transitions.get(current_status, []):
            raise serializers.ValidationError(
                f"Cannot transition from '{current_status}' to '{value}'."
            )
        return value