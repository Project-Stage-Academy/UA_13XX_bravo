from django.urls import re_path
from .consumers import ChatConsumer

websocket_urlpatterns = [
    re_path(
        r"ws/chat/(?P<company_id_1>\d+)/(?P<company_id_2>\d+)/$", ChatConsumer.as_asgi()
    ),
]
