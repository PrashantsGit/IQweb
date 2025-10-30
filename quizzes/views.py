from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required 
from django.utils import timezone
from django.db.models import Max
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

@login_required
def take_question(request, attempt_id, question_num):
    """
    Displays the current question and processes the answer submission.
    """
    attempt = get_object_or_404(UserTestAttempt, pk=attempt_id, user=request.user, is_completed=False)
    
    # Check if the test time has expired
    time_limit = attempt.test.duration * 60 
    elapsed_seconds = (timezone.now() - attempt.start_time).total_seconds()
    
    if elapsed_seconds > time_limit:
        # Time expired: Redirect to submission/scoring
        return redirect('test_submit', attempt_id=attempt.pk)
        
    # --- Determine the current question ---
    # Fetch ALL questions for the test, ordered by primary key (or an 'order' field if you added one)
    questions = attempt.test.questions.all().order_by('pk')
    total_questions = questions.count()
    
    if question_num > total_questions:
        # User has answered all questions: Redirect to submission
        return redirect('test_submit', attempt_id=attempt.pk)
        
    current_question = questions[question_num - 1] # question_num is 1-based index

    # --- Handle POST Request (Answer Submission) ---
    if request.method == 'POST':
        # 1. Process and save the answer
        
        # Check if an answer already exists for this question/attempt to prevent double submission
        UserAnswer.objects.filter(attempt=attempt, question=current_question).delete()

        # For Multiple Choice Questions (MCQ)
        if current_question.question_type == 'MC':
            selected_answer_id = request.POST.get('answer')
            if selected_answer_id:
                selected_answer = get_object_or_404(Answer, pk=selected_answer_id)
                is_correct = selected_answer.is_correct
                
                UserAnswer.objects.create(
                    attempt=attempt,
                    question=current_question,
                    selected_answer=selected_answer,
                    is_correct=is_correct
                )
        
        # NOTE: Logic for 'VI' or 'LG' question types would go here (using request.POST.get('text_input'))

        # 2. Redirect to the next question
        next_question_num = question_num + 1
        return redirect('take_question', attempt_id=attempt.pk, question_num=next_question_num)

    # --- Handle GET Request (Display Question) ---
    else:
        # Calculate time remaining for display
        remaining_seconds = int(time_limit - elapsed_seconds)
        
        context = {
            'attempt': attempt,
            'question': current_question,
            'answers': current_question.answers.all(), # Options for MCQ
            'question_num': question_num,
            'total_questions': total_questions,
            'remaining_time': remaining_seconds,
            'progress_percent': int((question_num - 1) / total_questions * 100) if total_questions else 0,
        }
        return render(request, 'quizzes/take_question.html', context)