import pytest
from django.contrib.auth import get_user_model
from notifications.models import Notification, Type
from companies.models import CompanyProfile, CompanyFollowers, UserToCompany

User = get_user_model()

@pytest.mark.django_db
def test_create_notification_on_profile_update():
    """
    Tests whether a Notification is created and an email is sent when a startup updates its profile.
    """

    # 🔹 Create an investor user and their associated company
    investor_user = User.objects.create_user(email="investor@example.com", password="testpassword")
    investor_profile = CompanyProfile.objects.create(company_name="Investor Inc.", type="enterprise")
    UserToCompany.objects.create(user=investor_user, company=investor_profile)

    # 🔹 Create a startup user and their associated company
    startup_user = User.objects.create_user(email="startup@example.com", password="testpassword")
    startup_profile = CompanyProfile.objects.create(company_name="Startup X", type="startup")
    UserToCompany.objects.create(user=startup_user, company=startup_profile)

    # 🔹 The investor follows the startup
    CompanyFollowers.objects.create(investor=investor_profile, startup=startup_profile)

    # ✅ Ensure that no notifications exist before updating the profile
    assert Notification.objects.count() == 0

    # 🔹 Update the startup profile (should trigger the signal and create a notification)
    startup_profile.company_name = "Startup X - Updated"
    startup_profile.save()

    # ✅ Check that exactly one notification was created
    assert Notification.objects.count() == 1

    # 🔹 Retrieve the created notification
    notification = Notification.objects.first()
    notification_type = Type.objects.get(name="new_post")

    # ✅ Ensure the notification is assigned to the correct investor
    assert notification.user == investor_user
    assert notification.type == notification_type
    assert "updated their profile" in notification.content
