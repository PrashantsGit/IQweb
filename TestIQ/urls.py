

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from quizzes import views as quiz_views

urlpatterns = [
    # Landing Page
    path('', quiz_views.landing, name='landing'),

    # Auth routes
    path('login/', quiz_views.custom_login, name='login'),
    path('register/', quiz_views.register, name='register'),
    path('logout/', quiz_views.custom_login, name='logout'),

    # Include quiz URLs under their own namespace (NO conflict)
    path('', include('quizzes.urls')),   # ← this is OK now because '/' is handled above
    
    # Admin
    path('admin/', admin.site.urls),
]

# Media files
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
