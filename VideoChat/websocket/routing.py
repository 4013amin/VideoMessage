# app/routing.py
from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    re_path(r'wss/video-call/$', consumers.VideoCallConsumer.as_asgi()),
]
