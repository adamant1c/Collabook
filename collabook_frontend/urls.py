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
from core import views as core_views

def ads_txt(request):
    return HttpResponse("google.com, pub-9623905672643205, DIRECT, f08c47fec0942fa0", content_type="text/plain")

def robots_txt(request):
    lines = [
        "User-agent: *",
        "Allow: /ads.txt",
        "Allow: /",
        "",
        "Sitemap: https://collabook.click/sitemap.xml",
    ]
    return HttpResponse("\n".join(lines), content_type="text/plain")

def sitemap_xml(request):
    xml_content = """<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
  <url>
    <loc>https://collabook.click/</loc>
    <priority>1.0</priority>
  </url>
  <url>
    <loc>https://collabook.click/about/</loc>
    <priority>0.8</priority>
  </url>
  <url>
    <loc>https://collabook.click/game/rules/</loc>
    <priority>0.8</priority>
  </url>
  <url>
    <loc>https://collabook.click/accounts/register/</loc>
    <priority>0.7</priority>
  </url>
</urlset>"""
    return HttpResponse(xml_content, content_type="application/xml")

urlpatterns = [
    path('admin/', admin.site.urls),
    path('i18n/', include('django.conf.urls.i18n')),
    path('ads.txt', ads_txt),
    path('robots.txt', robots_txt),
    path('sitemap.xml', sitemap_xml),
    path('accounts/', include('allauth.urls')),
    path('', include('accounts.urls')),
    path('character/', include('character.urls')),
    path('world/', include('world.urls')),
    path('game/', include('game.urls')),
    path('about/', core_views.about, name='about'),
]
