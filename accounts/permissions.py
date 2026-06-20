from rest_framework.permissions import BasePermission


class IsEmployer(BasePermission):
    """
    Allows access only to users with role 'employer'.
    """
    message = "Only employers can perform this action."

    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and request.user.role == 'employer'
        )


class IsCandidate(BasePermission):
    """
    Allows access only to users with role 'candidate'.
    """
    message = "Only candidates can perform this action."

    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and request.user.role == 'candidate'
        )