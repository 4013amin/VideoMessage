# websocket/views.py
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages

def home_view(request):
    if request.user.is_authenticated:
        return redirect('video_call')
    return redirect('account_login')

@login_required(login_url='/accounts/login/') 
def video_call_view(request):
    return render(request, 'index.html')

def handler404(request, exception):
    return render(request, '404.html', status=404)

def handler500(request):
    return render(request, '500.html', status=500)