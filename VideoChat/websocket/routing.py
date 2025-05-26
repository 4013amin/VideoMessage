from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    re_path(r'wss/video/(?P<username>\w+)/$', consumers.VideoCallConsumer.as_asgi()),
]
