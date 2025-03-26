from django.urls import re_path
from .chat import Chat

websocket_urlpatterns = [
    re_path(r"ws/chat/$", Chat.as_asgi()),
]
