from django.contrib.auth.signals import user_logged_in
from django.dispatch import receiver
from social_django.models import UserSocialAuth
from django.contrib.auth import get_user_model

User = get_user_model()

@receiver(user_logged_in)
def save_google_user(sender, user, request, **kwargs):
    if user and 'google-oauth2' in kwargs.get('backend', ''):
        social = user.social_auth.get(provider='google-oauth2')
        user.google_id = social.uid
        user.email = social.extra_data.get('email', '')
        user.display_name = social.extra_data.get('name', '')
        user.profile_picture = social.extra_data.get('picture', '')
        user.save()