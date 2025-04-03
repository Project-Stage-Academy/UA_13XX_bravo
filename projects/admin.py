from django.contrib import admin

from projects.models import Project

class ProjectAdmin(admin.ModelAdmin):
    list_display = ('name', 'status', 'information', 'created_at', 'updated_at')
    search_fields = ('name', 'information')
    list_filter = ('created_at', 'updated_at')
    ordering = ('-created_at',)


admin.site.register(Project, ProjectAdmin)