from django.urls import path
from . import views

urlpatterns = [
    path('', views.test_list, name='test_list'),
    path('test/<int:pk>/start/', views.test_start, name='test_start'),
    path('attempt/<int:attempt_id>/question/<int:question_id>/', views.take_question, name='take_question'),
    path('attempt/<int:attempt_id>/submit/', views.test_submit, name='test_submit'),
    path('dashboard/', views.user_dashboard, name='user_dashboard'),
    path('register/', views.register, name='register'),
]
