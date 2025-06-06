from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from allauth.socialaccount.models import SocialAccount

def get_user_display_info(request):
    """Helper function to get user display information"""
    if request.user.is_authenticated:
        social_account = SocialAccount.objects.filter(user=request.user).first()
        
        if social_account and social_account.provider == 'google':
            # Use Google account info if available
            extra_data = social_account.extra_data
            display_name = extra_data.get('name', request.user.username)
            avatar_url = extra_data.get('picture', None)
        else:
            # Fallback to standard user info
            display_name = request.user.get_full_name() or request.user.username
            avatar_url = None
            
        return {
            'display_name': display_name,
            'avatar_url': avatar_url,
            'is_authenticated': True,
            'email': request.user.email,
        }
    return {
        'display_name': "مهمان",
        'avatar_url': None,
        'is_authenticated': False,
        'email': None,
    }

@login_required(login_url='/accounts/google/login/')
def video_call_view(request):
    try:
        context = get_user_display_info(request)
        context['page_title'] = "اتصال ویدیویی StarCall"
    
        
        return render(request, 'index.html', context)
    
    except Exception as e:
        messages.error(request, "خطایی در بارگذاری صفحه رخ داد. لطفاً دوباره تلاش کنید.")
        return render(request, 'error.html', status=500)

def home_view(request):
    """Home page view with login options"""
    context = get_user_display_info(request)
    context['page_title'] = "خوش آمدید به StarCall"
    return render(request, 'index.html', context)

def handler404(request, exception):
    """Custom 404 handler"""
    return render(request, '404.html', status=404)

def handler500(request):
    """Custom 500 handler"""
    return render(request, '500.html', status=500)