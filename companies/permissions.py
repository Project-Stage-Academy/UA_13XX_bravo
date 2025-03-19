from rest_framework.permissions import BasePermission
from companies.models import UserToCompany

class IsCompanyMember(BasePermission):
    """
    Grants access only to users associated with the selected company.
    """
    def has_permission(self, request, view) -> bool:
        """
        Check if the user is associated with the selected company.

        Args:
            request: The HTTP request object.
            view: The view that is being accessed.

        Returns:
            bool: True if the user is associated with the company, False otherwise.
        """
        company_id = request.headers.get("X-Company-ID", getattr(request, "company_id", None))

        if not company_id or not UserToCompany.objects.filter(user=request.user, company_id=company_id).exists():
            return False

        request.company_id = company_id
        return True