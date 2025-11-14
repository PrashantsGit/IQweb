# TestIQ/urls.py

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.shortcuts import render

from quizzes import views as quiz_views


# Landing page view
def landing_page(request):
    return render(request, "quizzes/landing.html")


urlpatterns = [
    # Landing Page
    path('', landing_page, name='landing'),

    # Custom Auth Routes (use your custom templates)
    path('login/', quiz_views.custom_login, name='login'),
    path('register/', quiz_views.register, name='register'),

    # Include Django's default auth (logout, password reset)
    path('accounts/', include('django.contrib.auth.urls')),

    # Quizzes App URLs
    path('', include('quizzes.urls')),

    # Admin
    path('admin/', admin.site.urls),
]


# Media (for images)
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
