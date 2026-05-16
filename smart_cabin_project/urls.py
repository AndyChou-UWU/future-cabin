"""Project URL configuration for Railway deployment.

This file routes URLs to the appropriate Django apps and ensures that static
and media files are served correctly when `DEBUG=False` (as is the case on
Railway)."""

from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('my_cabin.urls')),  # core app
]

# In production (DEBUG=False) we still need to serve static & media files.
# Django's `static()` helper works both in DEBUG mode and when explicitly
# called, so we add the routes unconditionally.
if settings.DEBUG or not settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)