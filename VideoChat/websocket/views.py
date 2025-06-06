# websocket/views.py
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages

def home_view(request):
    # اگر کاربر لاگین کرده باشد، او را به صفحه تماس هدایت می‌کنیم
    if request.user.is_authenticated:
        return redirect('video_call')
    # در غیر این صورت، او را به صفحه لاگین هدایت می‌کنیم
    return redirect('account_login')

@login_required(login_url='/accounts/login/') # آدرس لاگین allauth
def video_call_view(request):
    # حالا که کاربر حتما لاگین کرده، مستقیم تمپلیت را رندر می‌کنیم
    return render(request, 'index.html')

# این ویوها را هم اصلاح می‌کنیم تا از تمپلیت‌های سفارشی استفاده کنند
def handler404(request, exception):
    return render(request, '404.html', status=404)

def handler500(request):
    return render(request, '500.html', status=500)