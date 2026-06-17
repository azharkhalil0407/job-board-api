from django.contrib import admin
from .models import Job, Application


class ApplicationInline(admin.TabularInline):
    model = Application
    extra = 0
    fields = ['candidate', 'status', 'applied_at']
    readonly_fields = ['applied_at']
    can_delete = False


@admin.register(Job)
class JobAdmin(admin.ModelAdmin):
    list_display = ['title', 'employer', 'status', 'location', 'created_at', 'application_count']
    list_filter = ['status', 'created_at']
    search_fields = ['title', 'description']
    inlines = [ApplicationInline]

    def application_count(self, obj):
        return obj.applications.count()
    application_count.short_description = 'Applications'


@admin.register(Application)
class ApplicationAdmin(admin.ModelAdmin):
    list_display = ['candidate', 'job', 'status', 'applied_at']
    list_filter = ['status', 'applied_at']
    search_fields = ['candidate__username', 'job__title']
    list_select_related = ['candidate', 'job']   # N+1 fix