from django.urls import path, include
from rest_framework.routers import DefaultRouter

from projects.views import ProjectViewSet


router = DefaultRouter()
router.register(r"projects", ProjectViewSet, basename='projects')

app_name = 'projects'

urlpatterns = [
    path("", include(router.urls)),
]
