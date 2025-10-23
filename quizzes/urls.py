
from django.urls import path
from . import views

urlpatterns = [
    # URL for listing all available tests
    path('', views.test_list, name='test_list'),
    
    
]