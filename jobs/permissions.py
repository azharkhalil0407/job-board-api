from rest_framework.permissions import BasePermission


class IsJobOwner(BasePermission):
    """
    Object-level permission. Allows access only to the employer
    who owns the job posting.
    """
    message = "You can only modify your own job postings."

    def has_object_permission(self, request, view, obj):
        return obj.employer == request.user


class IsApplicationOwner(BasePermission):
    """
    Object-level permission. Allows access only to the candidate
    who submitted the application.
    """
    message = "You can only access your own applications."

    def has_object_permission(self, request, view, obj):
        return obj.candidate == request.user


class IsApplicationJobOwner(BasePermission):
    """
    Object-level permission. Allows access only to the employer
    who owns the job the application belongs to.
    """
    message = "You can only manage applications for your own job postings."

    def has_object_permission(self, request, view, obj):
        return obj.job.employer == request.user