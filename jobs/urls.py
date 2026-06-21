from django.urls import path
from .views import (
    JobListCreateView,
    JobRetrieveUpdateDestroyView,
    JobApplyView,
    ApplicationListView,
    ApplicationRetrieveView,
    ApplicationStatusUpdateView,
)

urlpatterns = [
    # Job endpoints
    path('', JobListCreateView.as_view(), name='job-list-create'),
    path('<int:pk>/', JobRetrieveUpdateDestroyView.as_view(), name='job-detail'),

    # Application endpoints
    path('<int:pk>/apply/', JobApplyView.as_view(), name='job-apply'),
    path('applications/', ApplicationListView.as_view(), name='application-list'),
    path('applications/<int:pk>/', ApplicationRetrieveView.as_view(), name='application-detail'),
    path('applications/<int:pk>/status/', ApplicationStatusUpdateView.as_view(), name='application-status'),
]