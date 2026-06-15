from django.contrib import admin
from .models import Job, Application

@admin.register(Job)
class JobAdmin(admin.ModelAdmin):
    list_display = ['title', 'employer', 'status', 'location', 'created_at']
    list_filter = ['status']
    search_fields = ['title', 'description']

@admin.register(Application)
class ApplicationAdmin(admin.ModelAdmin):
    list_display = ['candidate', 'job', 'status', 'applied_at']
    list_filter = ['status']