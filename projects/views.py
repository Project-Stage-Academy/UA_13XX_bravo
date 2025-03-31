from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated
from companies.permissions import IsCompanyMember

from projects.models import Project
from projects.serializers import ProjectCreateUpdateSerializer, ProjectListSerializer


class ProjectViewSet(ModelViewSet):
    http_method_names = ("get", "post", "put", "delete")
    serializer_class = ProjectListSerializer
    permission_classes = [IsAuthenticated]
    queryset = Project.objects.all()

    def get_permissions(self):
        match (self.action):
            case "update" | "partial_update" | "destroy":
                return [IsAuthenticated(), IsCompanyMember()]
            case _:
                return super().get_permissions()

    def get_queryset(self):
        company_id = self.request.query_params.get("company_id")
        if company_id:
            return super().get_queryset().filter(company=company_id)

        return super().get_queryset()

    def get_serializer(self, *args, **kwargs):
        match (self.action):
            case "create" | "update" | "partial_update":
                kwargs["context"] = self.get_serializer_context()
                return ProjectCreateUpdateSerializer(*args, **kwargs)
            case _:
                return super().get_serializer(*args, **kwargs)
