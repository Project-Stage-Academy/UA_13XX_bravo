from django.urls import path
from .views import CreateChatRoomView

urlpatterns = [
    path("create-room/", CreateChatRoomView.as_view(), name="create-room"),
]
