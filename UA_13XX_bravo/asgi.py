"""
ASGI config for UA_13XX_bravo project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.1/howto/deployment/asgi/
"""

import os

from django.core.asgi import get_asgi_application

from channels.routing import ProtocolTypeRouter, URLRouter
from django.core.asgi import get_asgi_application
import communications.routing
from communications.middleware.jwt_auth import JWTAuthMiddleware

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "UA_13XX_bravo.settings")

django_asgi_app = get_asgi_application()

application = ProtocolTypeRouter(
    {
        "http": django_asgi_app,
        "websocket": JWTAuthMiddleware(
            URLRouter(communications.routing.websocket_urlpatterns)
        ),
    }
)
