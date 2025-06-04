from django.urls import path
from . import views

app_name = 'videochat'

urlpatterns = [
    path('', views.home_view, name='home'),
    path('video-call/', views.video_call_view, name='video_call'),
]