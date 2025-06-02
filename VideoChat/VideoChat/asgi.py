import os
from django.core.asgi import get_asgi_application
from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
import websocket.routing

# ⚠️ این خط بسیار مهم است!
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'VideoChat.settings')

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": AuthMiddlewareStack(
        URLRouter(
            websocket.routing.websocket_urlpatterns
        )
    ),
})
