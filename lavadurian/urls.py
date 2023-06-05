"""lavadurian URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
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
# from django.contrib import admin
# from django.urls import path, include

# urlpatterns = [
#     path('admin/', admin.site.urls),
#     path('', include('myapp.urls')),
# ]

from django.conf import settings
from django.conf.urls.static import static
from django.views.static import serve
from django.conf.urls import url
from rest_framework import routers

from django.contrib import admin
from django.urls import path, include
import Pages
import Members
import Store
import Cart
import DurianAPI

admin.autodiscover()
admin.site.enable_nav_sidebar = False

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('allauth.urls')),

    # add this two lines for password reset using rest-api
    url(r'^dj-rest-auth/', include('dj_rest_auth.urls')),
    url(r'^', include('django.contrib.auth.urls')),

    path('', include('Pages.urls')),
    path('', include('Members.urls')),
    path('', include('News.urls')),
    path('', include('Store.urls')),
    path('', include('Cart.urls')),
    path('', include('DurianAPI.urls')),
    path('', include('chatbot.urls')),
]

# Serv Static file on debug and production
# For display Media or Image
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL,
                          document_root=settings.MEDIA_ROOT)
else:
    # for production
    urlpatterns += [
        url(r'^uploads/(?P<path>.*)$', serve,
            {'document_root': settings.MEDIA_ROOT}),
        url(r'^static/(?P<path>.*)$', serve,
            {'document_root': settings.STATIC_ROOT}),
    ]
