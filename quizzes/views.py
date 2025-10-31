# quizzes/views.py

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from .models import Test, UserTestAttempt, Question, Answer, UserAnswer 

def test_list(request):
    """Displays a list of all available IQ tests."""
    tests = Test.objects.all().order_by('title')
    context = {
        'tests': tests,
        'title': 'Available IQ Tests'
    }
    return render(request, 'quizzes/test_list.html', context)

@login_required 
def test_start(request, test_id):
    """
    Handles the start of a test session by creating a UserTestAttempt 
    and redirects to the first question.
    """
    test = get_object_or_404(Test, pk=test_id)
    
    try:
        # Check for an existing, incomplete attempt
        attempt = UserTestAttempt.objects.get(
            user=request.user, 
            test=test, 
            is_completed=False
        )
    except UserTestAttempt.DoesNotExist:
        # Create a new attempt
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
    # Ensure the attempt belongs to the user and is not completed
    attempt = get_object_or_404(UserTestAttempt, pk=attempt_id, user=request.user, is_completed=False)
    
    # --- Time Check (Server-side defense) ---
    time_limit = attempt.test.duration * 60 # Convert minutes to seconds
    elapsed_seconds = (timezone.now() - attempt.start_time).total_seconds()
    
    if elapsed_seconds > time_limit:
        # Time expired: Immediately redirect to submission
        return redirect('test_submit', attempt_id=attempt.pk)
        
    # --- Question Sequencing ---
    questions = attempt.test.questions.all().order_by('pk')
    total_questions = questions.count()
    
    if question_num > total_questions:
        # User has finished all questions: Redirect to submission
        return redirect('test_submit', attempt_id=attempt.pk)
        
    current_question = questions[question_num - 1] # 1-based index to 0-based list index

    # --- Handle POST Request (Answer Submission) ---
    if request.method == 'POST':
        # 1. Delete previous answer for this question (to handle back/forward logic if implemented)
        UserAnswer.objects.filter(attempt=attempt, question=current_question).delete()

        is_correct = False

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
        
        # NOTE: Logic for 'LG' or 'VI' (text_input) comparison would be here
        # E.g., elif current_question.question_type == 'LG': ...

        # 2. Redirect to the next question
        next_question_num = question_num + 1
        return redirect('take_question', attempt_id=attempt.pk, question_num=next_question_num)

    # --- Handle GET Request (Display Question) ---
    else:
        remaining_seconds = int(time_limit - elapsed_seconds)
        
        context = {
            'attempt': attempt,
            'question': current_question,
            'answers': current_question.answers.all(), 
            'question_num': question_num,
            'total_questions': total_questions,
            'remaining_time': remaining_seconds,
            'progress_percent': int((question_num - 1) / total_questions * 100) if total_questions else 0,
        }
        return render(request, 'quizzes/take_question.html', context)


@login_required
def test_submit(request, attempt_id):
    """
    Finalizes the test attempt, calculates the score, and saves the result.
    """
    attempt = get_object_or_404(UserTestAttempt, pk=attempt_id, user=request.user)

    # 1. If already scored, just show the results
    if attempt.is_completed:
        total_questions = attempt.test.questions.count()
        correct_count = attempt.answers.filter(is_correct=True).count()
        score_percentage = (correct_count / total_questions) * 100 if total_questions else 0
        return render(request, 'quizzes/results.html', {
            'attempt': attempt,
            'correct_count': correct_count,
            'total_questions': total_questions,
            'score_percentage': score_percentage,
        })


    # 2. Calculate Score
    correct_count = attempt.answers.filter(is_correct=True).count()
    total_questions = attempt.test.questions.count()
    score_percentage = (correct_count / total_questions) * 100 if total_questions else 0
    
    # 3. Update Attempt Record
    attempt.score = int(score_percentage)
    attempt.is_completed = True
    attempt.end_time = timezone.now()
    attempt.save()

    # 4. Render Results
    return render(request, 'quizzes/results.html', {
        'attempt': attempt,
        'correct_count': correct_count,
        'total_questions': total_questions,
        'score_percentage': score_percentage,
    })

 @login_required
def user_dashboard(request):
    """
    Displays the user's profile and history of completed test attempts.
    """
    # Fetch all completed attempts for the current user, ordered newest first
    completed_attempts = UserTestAttempt.objects.filter(
        user=request.user, 
        is_completed=True
    ).order_by('-end_time')

    # Optionally, calculate average score across all completed tests
    total_score = sum(a.score for a in completed_attempts if a.score is not None)
    average_score = total_score / completed_attempts.count() if completed_attempts.count() > 0 else 0

    context = {
        'completed_attempts': completed_attempts,
        'average_score': round(average_score, 1),
    }

    return render(request, 'quizzes/user_dashboard.html', context)