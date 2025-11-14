from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    # Custom Register Page
    path('register/', views.register, name='register'),

    # Custom Login Page
    path('login/', auth_views.LoginView.as_view(
        template_name='quizzes/login.html'), 
        name='login'
    ),

    # Logout
    path('logout/', auth_views.LogoutView.as_view(next_page='landing'), name='logout'),

    # Tests
    path('tests/', views.test_list, name='test_list'),
    path('dashboard/', views.user_dashboard, name='user_dashboard'),

    # Test flow
    path('test/<int:test_id>/start/', views.test_start, name='test_start'),
    path('attempt/<int:attempt_id>/question/<int:question_num>/', views.take_question, name='take_question'),
    path('test/submit/<int:attempt_id>/', views.test_submit, name='test_submit'),
    path('attempt/<int:attempt_id>/certificate/', views.download_certificate, name='download_certificate'),
]
