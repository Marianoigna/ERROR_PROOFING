"""
ASGI config for ERROR_PROOFING project.
"""

import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
import AIS_BOX.routing

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ERROR_PROOFING.settings')

application = ProtocolTypeRouter({
    'http': get_asgi_application(),
    'websocket': AuthMiddlewareStack(
        URLRouter(
            AIS_BOX.routing.websocket_urlpatterns
        )
    ),
})
