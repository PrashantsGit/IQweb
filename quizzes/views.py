from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required # Import this
from django.db import IntegrityError
from .models import Test, UserTestAttempt, Question, Answer, UserAnswer

def test_list(request):
    """Displays a list of all available IQ tests."""
    
    # Fetch all Test objects from the database
    tests = Test.objects.all().order_by('title')
    
    # Context dictionary to pass data to the template
    context = {
        'tests': tests,
        'title': 'Available IQ Tests'
    }
    
    # Render the template
    return render(request, 'quizzes/test_list.html', context)

@login_required
def test_start(request, test_id):
    """
    Handles the start of a test session.
    Creates a UserTestAttempt object and redirects to the first question.
    """
    test = get_object_or_404(Test, pk=test_id)
    
    # Check for an existing, incomplete attempt
    try:
        attempt = UserTestAttempt.objects.get(
            user=request.user, 
            test=test, 
            is_completed=False
        )
        
    except UserTestAttempt.DoesNotExist:
        # Create a new attempt if none exists
        attempt = UserTestAttempt.objects.create(
            user=request.user,
            test=test
        )

    # Redirect to the first question (question number 1)
    return redirect('take_question', attempt_id=attempt.pk, question_num=1)