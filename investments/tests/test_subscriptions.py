import pytest
from rest_framework import status
from django.urls import reverse
from investments.models import Subscription


# =====================
#        CREATE
# =====================

@pytest.mark.django_db
def test_user_can_create_subscription(api_client, test_user):
    """User can create their own subscription"""
    api_client.force_authenticate(user=test_user)
    url = reverse("subscription-list")
    payload = {"investment_share": 25.5}

    response = api_client.post(url, data=payload, format="json")

    assert response.status_code == status.HTTP_201_CREATED
    assert Subscription.objects.count() == 1
    subscription = Subscription.objects.first()
    assert float(subscription.investment_share) == 25.5
    assert subscription.creator == test_user


# =====================
#        READ
# =====================

@pytest.mark.django_db
def test_user_cannot_see_others_subscriptions(api_client, test_user, another_user):
    """User cannot see subscriptions created by others"""
    Subscription.objects.create(investment_share=40.0, creator=another_user)

    api_client.force_authenticate(user=test_user)
    url = reverse("subscription-list")
    response = api_client.get(url)

    assert response.status_code == status.HTTP_200_OK
    assert response.data == []


@pytest.mark.django_db
def test_user_can_retrieve_own_subscription(api_client, test_user):
    """User can retrieve details of their own subscription"""
    subscription = Subscription.objects.create(investment_share=15.0, creator=test_user)

    api_client.force_authenticate(user=test_user)
    url = reverse("subscription-detail", args=[subscription.pk])
    response = api_client.get(url)

    assert response.status_code == status.HTTP_200_OK
    assert response.data["investment_share"] == "15.00"


@pytest.mark.django_db
def test_user_cannot_retrieve_others_subscription(api_client, test_user, another_user):
    """User cannot retrieve details of subscriptions owned by others"""
    subscription = Subscription.objects.create(investment_share=99.9, creator=another_user)

    api_client.force_authenticate(user=test_user)
    url = reverse("subscription-detail", args=[subscription.pk])
    response = api_client.get(url)

    assert response.status_code == status.HTTP_404_NOT_FOUND


# =====================
#       UPDATE
# =====================

@pytest.mark.django_db
def test_user_cannot_update_others_subscription(api_client, test_user, another_user):
    """User cannot update subscriptions created by others"""
    subscription = Subscription.objects.create(investment_share=10.0, creator=another_user)

    api_client.force_authenticate(user=test_user)
    url = reverse("subscription-detail", args=[subscription.pk])
    payload = {"investment_share": 50.0}

    response = api_client.put(url, data=payload, format="json")

    assert response.status_code == status.HTTP_403_FORBIDDEN


# =====================
#       DELETE
# =====================

@pytest.mark.django_db
def test_user_cannot_delete_others_subscription(api_client, test_user, another_user):
    """User cannot delete subscriptions created by others"""
    subscription = Subscription.objects.create(investment_share=30.0, creator=another_user)

    api_client.force_authenticate(user=test_user)
    url = reverse("subscription-detail", args=[subscription.pk])
    response = api_client.delete(url)

    assert response.status_code == status.HTTP_403_FORBIDDEN