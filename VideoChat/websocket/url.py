from django.urls import path
from .views import video_test_view
from django.http import HttpResponse

def health_check(request):
    return HttpResponse("OK", status=200)


urlpatterns = [
    path('', video_test_view),
    
    path('health/', health_check, name='health_check'),
    path('', lambda request: HttpResponse(open('templates/index.html').read(), content_type='text/html'), name='index'),

]
