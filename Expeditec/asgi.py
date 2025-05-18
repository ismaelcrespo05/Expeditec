import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack

# 1️⃣ Define tu settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Expeditec.settings')

# 2️⃣ La app ASGI para HTTP
django_asgi_app = get_asgi_application()

# 3️⃣ Importa tus websocket_urlpatterns
from Chat.routing import websocket_urlpatterns

application = ProtocolTypeRouter({
    # HTTP (Django views)
    "http": django_asgi_app,

    # WebSocket (Channels)
    "websocket": AuthMiddlewareStack(
        URLRouter(
            websocket_urlpatterns
        )
    ),
})
