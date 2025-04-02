import pytest
from rest_framework import status
from django.urls import reverse
from investments.models import Subscription

@pytest.mark.django_db
def test_user_can_create_subscription(api_client, test_user):
    api_client.force_authenticate(user=test_user)
    url = reverse("subscription-list")  # because we registered a ViewSet with basename="subscription"
    payload = {
        "investment_share": 25.5
    }

    response = api_client.post(url, data=payload, format="json")

    assert response.status_code == status.HTTP_201_CREATED
    assert Subscription.objects.count() == 1
    subscription = Subscription.objects.first()
    assert float(subscription.investment_share) == 25.5
    assert subscription.creator == test_user