from django.urls import path
from .views import JobListCreateView, JobRetrieveUpdateDestroyView

urlpatterns = [
    path('', JobListCreateView.as_view(), name='job-list-create'),
    path('<int:pk>/', JobRetrieveUpdateDestroyView.as_view(), name='job-detail'),
]