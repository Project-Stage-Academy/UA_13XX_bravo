from django.urls import re_path
from .chat import Chat

#додав підключення до id_room
websocket_urlpatterns = [
    re_path(r"ws/chat/(?P<room_id>\w+)/$", Chat.as_asgi()),
]
