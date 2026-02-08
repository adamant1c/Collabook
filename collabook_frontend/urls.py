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
from django.views.generic import RedirectView

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
    from blog.models import Post
    from django.urls import reverse
    
    base_url = "https://collabook.click"
    static_pages = [
        ('/', 1.0, 'weekly'),
        ('/about/', 0.8, 'monthly'),
        ('/game/rules/', 0.8, 'monthly'),
        ('/world/selection/', 0.9, 'weekly'),
        ('/character/sheet/', 0.9, 'weekly'),
        ('/privacy-policy', 0.6, 'monthly'),
        ('/terms', 0.6, 'monthly'),
        ('/faq', 0.7, 'monthly'),
        ('/contact', 0.6, 'monthly'),
        ('/how-it-works', 0.7, 'monthly'),
        ('/blog/', 0.9, 'weekly'),
    ]
    
    xml_lines = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'
    ]
    
    # Add static pages
    for page, priority, freq in static_pages:
        xml_lines.append(f'  <url>')
        xml_lines.append(f'    <loc>{base_url}{page}</loc>')
        xml_lines.append(f'    <lastmod>2026-02-08</lastmod>')
        xml_lines.append(f'    <changefreq>{freq}</changefreq>')
        xml_lines.append(f'    <priority>{priority}</priority>')
        xml_lines.append(f'  </url>')
    
    # Add dynamic blog posts
    published_posts = Post.objects.filter(status=1).order_by('-created_on')
    for post in published_posts:
        xml_lines.append(f'  <url>')
        xml_lines.append(f'    <loc>{base_url}/blog/{post.slug}/</loc>')
        xml_lines.append(f'    <lastmod>{post.updated_on.strftime("%Y-%m-%d")}</lastmod>')
        xml_lines.append(f'    <changefreq>monthly</changefreq>')
        xml_lines.append(f'    <priority>0.8</priority>')
        xml_lines.append(f'  </url>')
    
    xml_lines.append('</urlset>')
    
    return HttpResponse("\n".join(xml_lines), content_type="application/xml")

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
    path('privacy-policy', core_views.privacy_policy, name='privacy_policy'),
    path('terms', core_views.terms, name='terms'),
    path('faq', core_views.faq, name='faq'),
    path('contact', RedirectView.as_view(url='/about/', permanent=True), name='contact'),
    path('how-it-works', core_views.how_it_works, name='how_it_works'),
    path('blog/', include('blog.urls')),
]

from django.conf import settings
from django.conf.urls.static import static

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

