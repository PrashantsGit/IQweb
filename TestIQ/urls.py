"""
URL configuration for TestIQ project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
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
# iq_test_site/urls.py

from django.contrib import admin
from django.urls import path, include
from django.conf import settings # New Import!
from django.conf.urls.static import static # New Import!
from django.shortcuts import render

def landing_page(request):
    return render(request, "quizzes/landing.html")

urlpatterns = [
    path('', landing_page, name='landing'),            # <-- HOMEPAGE
    path('', include('quizzes.urls')),                 
    path('accounts/', include('django.contrib.auth.urls')),
    path('admin/', admin.site.urls),
]

# 3. Serving media files during development (Crucial for question images)
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)