from django.urls import path
from . import views

urlpatterns = [
    path('tests/', views.test_list, name='test_list'),
    path('dashboard/', views.user_dashboard, name='user_dashboard'),

    # Test flow
    path('test/<int:test_id>/start/', views.test_start, name='test_start'),
    path('attempt/<int:attempt_id>/question/<int:question_num>/', views.take_question, name='take_question'),
    path('test/submit/<int:attempt_id>/', views.test_submit, name='test_submit'),
]
