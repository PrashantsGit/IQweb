# quizzes/urls.py

from django.urls import path
from . import views

urlpatterns = [
    # 1. Lists all available tests (already created)
    path('', views.test_list, name='test_list'),
    
    # 2. Page to start a specific test and begin the session
    path('<int:test_id>/start/', views.test_start, name='test_start'),

    # 3. View for presenting a specific question in the sequence
    path('<int:attempt_id>/question/<int:question_num>/', views.take_question, name='take_question'),

    # 4. View for submitting the final test
    path('<int:attempt_id>/submit/', views.test_submit, name='test_submit'),
]