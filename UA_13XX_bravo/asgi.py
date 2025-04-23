"""
ASGI config for UA_13XX_bravo project.
"""

import os
import django
import logging

# Set up basic logging
logger = logging.getLogger("django")

# Set the default Django settings module for ASGI
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "UA_13XX_bravo.settings")

# Initialize Django before importing anything that touches models/apps
django.setup()

from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from communications.middleware.jwt_auth import JWTAuthMiddleware
from communications.routing import websocket_urlpatterns  # Safe to import now

logger.debug(f"WebSocket routes loaded: {websocket_urlpatterns}")

# Define the ASGI application
application = ProtocolTypeRouter(
    {
        "http": get_asgi_application(),
        "websocket": JWTAuthMiddleware(URLRouter(websocket_urlpatterns)),
    }
)
