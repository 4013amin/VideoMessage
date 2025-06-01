from django.contrib import admin
from django.urls import path, include
from . import views

urlpatterns = [
    path('', views.video_call_view, name='video_call'),
    path('auth/', include('social_django.urls', namespace='social')),
]