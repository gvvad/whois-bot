from django.conf import settings
from django.conf.urls import include, url
from django.urls import path
from django.contrib import admin
from django.http import HttpResponse
import logging

from whoisbot.views import add_path

logging.basicConfig(level=logging.DEBUG if settings.DEBUG else logging.INFO)
logging.info("urls.py START")

def index(val):
    return HttpResponse("Index page for app!")

urlpatterns = [
    path("", index),
    url(r'^admin/', admin.site.urls),
] + add_path

if settings.DEBUG:
    import debug_toolbar
    urlpatterns = [
        url(r'^__debug__/', include(debug_toolbar.urls)),
    ] + urlpatterns

logging.info("urls.py END")
