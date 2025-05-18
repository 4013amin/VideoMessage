from django.urls import path
from .views import video_test_view

urlpatterns = [
    path("video-chat/", video_test_view),
]
