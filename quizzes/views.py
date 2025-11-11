from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from .models import Test, Question, Answer, UserTestAttempt, UserAnswer
import math
from datetime import timedelta
from django.db.models import Q
from collections import defaultdict


def register(request):
    """
    Handles user registration using Django's built-in UserCreationForm.
    Redirects to login after success.
    """
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, f'Account created for {user.username}! You can now log in.')
            return redirect('login')
        else:
            messages.error(request, "Please fix the errors below.")
    else:
        form = UserCreationForm()

    return render(request, 'registration/register.html', {'form': form})


@login_required
def test_list(request):
    tests = Test.objects.all()
    return render(request, 'quizzes/test_list.html', {'tests': tests})


@login_required
def test_start(request, pk):
    test = get_object_or_404(Test, pk=pk)
    attempt, created = UserTestAttempt.objects.get_or_create(user=request.user, test=test, is_completed=False)
    first_question = Question.objects.filter(test=test).first()
    return redirect('take_question', attempt_id=attempt.id, question_id=first_question.id)


@login_required
def take_question(request, attempt_id, question_id):
    attempt = get_object_or_404(UserTestAttempt, id=attempt_id, user=request.user)
    question = get_object_or_404(Question, id=question_id)
    answers = Answer.objects.filter(question=question)
    total_questions = Question.objects.filter(test=attempt.test).count()

    # 🕒 Auto-submit check
    allowed_end_time = attempt.start_time + timedelta(minutes=attempt.test.duration)
    now = timezone.now()
    if now > allowed_end_time:
        # Force submit
        attempt.end_time = allowed_end_time
        attempt.is_completed = True
        attempt.save()
        return redirect('test_submit', attempt_id=attempt.id)

    # Normal answer processing
    if request.method == 'POST':
        selected_answer_id = request.POST.get('answer')
        if selected_answer_id:
            selected_answer = Answer.objects.get(pk=selected_answer_id)
            UserAnswer.objects.update_or_create(
                attempt=attempt, question=question, defaults={'selected_answer': selected_answer}
            )

        next_question = Question.objects.filter(test=attempt.test, id__gt=question.id).first()
        if next_question:
            return redirect('take_question', attempt_id=attempt.id, question_id=next_question.id)
        else:
            return redirect('test_submit', attempt_id=attempt.id)

    progress_percent = int(
        (Question.objects.filter(test=attempt.test, id__lte=question.id).count() / total_questions) * 100
    )

    # Calculate remaining time (for JS display)
    remaining_seconds = max(0, int((allowed_end_time - now).total_seconds()))

    return render(request, 'quizzes/take_question.html', {
        'attempt': attempt,
        'question': question,
        'answers': answers,
        'question_num': Question.objects.filter(test=attempt.test, id__lte=question.id).count(),
        'total_questions': total_questions,
        'progress_percent': progress_percent,
        'remaining_time': remaining_seconds,  # ⏳ Updated dynamically
    })



@login_required
def test_submit(request, attempt_id):
    attempt = get_object_or_404(UserTestAttempt, id=attempt_id, user=request.user)
    answers = UserAnswer.objects.filter(attempt=attempt)
    questions = Question.objects.filter(test=attempt.test)
    total_questions = questions.count()

    correct_count = 0
    category_correct = defaultdict(int)
    category_total = defaultdict(int)

    for a in answers:
        q = a.question
        if a.selected_answer and a.selected_answer.is_correct:
            correct_count += 1
            category_correct[q.category] += 1
        category_total[q.category] += 1

    # Final overall score
    attempt.end_time = timezone.now()
    attempt.is_completed = True
    attempt.score = round((correct_count / total_questions) * 100, 1)

    # Time & speed factor for IQ
    time_taken = (attempt.end_time - attempt.start_time).total_seconds()
    avg_time = max(5, (attempt.test.duration * 60) / total_questions)
    accuracy = correct_count / total_questions
    speed_factor = max(0.8, min(1.2, avg_time / (time_taken / total_questions)))
    raw_score = (accuracy * 100) * speed_factor
    iq_score = 100 + ((raw_score - 70) * 15 / 10)
    attempt.iq_score = round(min(max(iq_score, 60), 160), 1)
    attempt.save()

    # 🧠 Category-wise IQ calculation
    category_iq = {}
    for cat, total in category_total.items():
        correct_ratio = category_correct[cat] / total if total else 0
        cat_score = correct_ratio * 100
        category_iq[cat] = round(100 + ((cat_score - 70) * 15 / 10), 1)

    category_labels = {
        'LR': 'Logical Reasoning',
        'NR': 'Numerical Reasoning',
        'VR': 'Verbal Reasoning',
        'SR': 'Spatial Reasoning',
        'MR': 'Memory'
    }

    category_results = [
        {'name': category_labels.get(k, k), 'iq': v, 'correct': category_correct[k], 'total': category_total[k]}
        for k, v in category_iq.items()
    ]

    return render(request, 'quizzes/results.html', {
        'attempt': attempt,
        'total_questions': total_questions,
        'correct_count': correct_count,
        'score_percentage': attempt.score,
        'iq_score': attempt.iq_score,
        'category_results': category_results
    })

@login_required
def user_dashboard(request):
    attempts = UserTestAttempt.objects.filter(user=request.user, is_completed=True)
    avg_score = round(sum(a.iq_score for a in attempts) / len(attempts), 1) if attempts else 0
    return render(request, 'quizzes/user_dashboard.html', {
        'completed_attempts': attempts,
        'average_score': avg_score
    })
