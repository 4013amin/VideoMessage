from django.urls import path
from . import consumers

websocket_urlpatterns = [
    path("ws/video-call/", consumers.VideoCallConsumer.as_asgi()),
]
