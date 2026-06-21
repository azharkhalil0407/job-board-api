import django_filters
from .models import Job


class JobFilter(django_filters.FilterSet):
    location = django_filters.CharFilter(
        field_name='location',
        lookup_expr='icontains',
    )
    status = django_filters.ChoiceFilter(
        field_name='status',
        choices=Job.Status.choices,
    )
    salary_min = django_filters.NumberFilter(
        field_name='salary_min',
        lookup_expr='gte',
    )
    salary_max = django_filters.NumberFilter(
        field_name='salary_max',
        lookup_expr='lte',
    )
    created_after = django_filters.DateFilter(
        field_name='created_at',
        lookup_expr='date__gte',
    )

    class Meta:
        model = Job
        fields = ['location', 'status', 'salary_min', 'salary_max', 'created_after']