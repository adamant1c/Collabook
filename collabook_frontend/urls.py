"""
URL configuration for collabook_frontend project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include

from django.http import HttpResponse

def ads_txt(request):
    return HttpResponse("google.com, pub-9623905672643205, DIRECT, f08c47fec0942fa0", content_type="text/plain")

urlpatterns = [
    path('admin/', admin.site.urls),
    path('i18n/', include('django.conf.urls.i18n')),
    path('ads.txt', ads_txt),
    path('accounts/', include('allauth.urls')),
    path('', include('accounts.urls')),
    path('character/', include('character.urls')),
    path('world/', include('world.urls')),
    path('game/', include('game.urls')),
]
