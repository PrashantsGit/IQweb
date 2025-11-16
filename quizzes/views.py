# quizzes/views.py

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib import messages
from django.contrib.auth import login as auth_login
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.db.models import Q

from .models import Test, Question, Answer, UserTestAttempt, UserAnswer

import math
from io import BytesIO
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.colors import HexColor
from django.utils import timezone   # ✅ FIXED — timezone-safe

# -----------------------------
# REGISTER VIEW
# -----------------------------
def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, "Account created successfully! You may now log in.")
            return redirect('login')
        else:
            messages.error(request, "Please fix the errors below.")
    else:
        form = UserCreationForm()

    return render(request, "registration/register.html", {'form': form})


# -----------------------------
# CUSTOM LOGIN VIEW
# -----------------------------
def custom_login(request):
    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)

        if form.is_valid():
            user = form.get_user()
            auth_login(request, user)
            return redirect('user_dashboard')
        else:
            messages.error(request, "Invalid username or password.")
    else:
        form = AuthenticationForm()

    return render(request, "registration/login.html", {'form': form})


# -----------------------------
# TEST LIST PAGE
# -----------------------------
@login_required
def test_list(request):
    tests = Test.objects.all()
    return render(request, "quizzes/test_list.html", {"tests": tests})


# -----------------------------
# START TEST
# -----------------------------
@login_required
def test_start(request, test_id):
    test = get_object_or_404(Test, pk=test_id)

    # Create a test attempt (timezone-safe)
    attempt = UserTestAttempt.objects.create(
        user=request.user,
        test=test,
        start_time=timezone.now()    # ✅ FIXED
    )

    return redirect('take_question', attempt_id=attempt.id, question_num=1)


# -----------------------------
# TAKE QUESTION
# -----------------------------
@login_required
def take_question(request, attempt_id, question_num):
    attempt = get_object_or_404(UserTestAttempt, pk=attempt_id)
    questions = Question.objects.filter(test=attempt.test).order_by('id')
    total_questions = len(questions)

    # Test complete
    if question_num > total_questions:
        return redirect('test_submit', attempt_id=attempt.id)

    question = questions[question_num - 1]
    answers = Answer.objects.filter(question=question)

    # Remaining time logic (timezone-safe)
    elapsed = (timezone.now() - attempt.start_time).total_seconds()   # ✅ FIXED
    remaining_time = attempt.test.duration * 60 - elapsed

    if remaining_time <= 0:
        return redirect('test_submit', attempt_id=attempt.id)

    if request.method == "POST":
        selected = request.POST.get("answer")

        UserAnswer.objects.update_or_create(
            attempt=attempt,
            question=question,
            defaults={"selected_answer_id": selected}
        )

        return redirect('take_question', attempt_id=attempt.id, question_num=question_num + 1)

    progress_percent = int((question_num - 1) / total_questions * 100)

    return render(request, "quizzes/take_question.html", {
        "attempt": attempt,
        "question": question,
        "answers": answers,
        "question_num": question_num,
        "total_questions": total_questions,
        "progress_percent": progress_percent,
        "remaining_time": int(remaining_time),
    })


# -----------------------------
# SUBMIT TEST
# -----------------------------
@login_required
def test_submit(request, attempt_id):
    from django.utils import timezone

    attempt = get_object_or_404(UserTestAttempt, pk=attempt_id)

    # Get all questions from this test
    questions = Question.objects.filter(test=attempt.test)
    total_questions = questions.count()

    # Fetch all user answers (with selected_answer prefetched)
    user_answers = UserAnswer.objects.filter(attempt=attempt).select_related("selected_answer", "question")

    # ------------------------------
    # 1. COUNT CORRECT ANSWERS
    # ------------------------------
    correct_count = 0
    for ua in user_answers:
        if ua.selected_answer and ua.selected_answer.is_correct:
            correct_count += 1

    # Percentage score
    if total_questions > 0:
        score_percentage = round((correct_count / total_questions) * 100, 1)
    else:
        score_percentage = 0

    # ------------------------------
    # 2. WEIGHTED SCORING BASED ON DIFFICULTY
    # ------------------------------
    difficulty_weights = {"E": 1, "M": 2, "H": 3}

    weighted_score = 0
    max_weight = 0

    for q in questions:
        max_weight += difficulty_weights[q.difficulty]

    for ua in user_answers:
        if ua.selected_answer and ua.selected_answer.is_correct:
            weighted_score += difficulty_weights[ua.question.difficulty]

    if max_weight > 0:
        ratio = weighted_score / max_weight  # 0..1 range
    else:
        ratio = 0

    # ------------------------------
    # 3. REALISTIC IQ CALCULATION (Gaussian)
    # ------------------------------
    # Convert ratio to Z-score
    Z = (ratio - 0.5) * 3.2    # spreads nicely across typical human distribution

    # Convert Z-score to IQ (mean=100, std dev=15)
    iq_score = int(100 + 15 * Z)

    # Hard limits for human IQ range
    iq_score = max(60, min(160, iq_score))

    # ------------------------------
    # 4. CATEGORY BREAKDOWN
    # ------------------------------
    categories = {
        "NR": "Numerical",
        "VR": "Verbal",
        "LR": "Logical",
        "SR": "Spatial",
        "MR": "Memory",
    }

    category_results = []

    for code, name in categories.items():
        cat_questions = questions.filter(category=code)
        total_cat = cat_questions.count()

        if total_cat == 0:
            continue

        correct_cat = user_answers.filter(
            question__category=code,
            selected_answer__is_correct=True
        ).count()

        # Category IQ scaling
        cat_ratio = correct_cat / total_cat
        cat_iq = int(60 + cat_ratio * 100)  # simplified for categories

        category_results.append({
            "name": name,
            "correct": correct_cat,
            "total": total_cat,
            "iq": cat_iq,
        })

    # ------------------------------
    # 5. SAVE ATTEMPT
    # ------------------------------
    attempt.score = score_percentage
    attempt.iq_score = iq_score
    attempt.end_time = timezone.now()
    attempt.is_completed = True
    attempt.save()

    # ------------------------------
    # 6. RENDER RESULTS PAGE
    # ------------------------------
    return render(request, "quizzes/results.html", {
        "attempt": attempt,
        "correct_count": correct_count,
        "total_questions": total_questions,
        "score_percentage": score_percentage,
        "iq_score": iq_score,
        "category_results": category_results,
    })




# -----------------------------
# DOWNLOAD CERTIFICATE (PDF)
# -----------------------------
@login_required
def download_certificate(request, attempt_id):
    attempt = get_object_or_404(UserTestAttempt, pk=attempt_id)

    buffer = BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=A4)

    pdf.setFont("Helvetica-Bold", 24)
    pdf.drawString(100, 750, "IQ Test Certificate")

    pdf.setFont("Helvetica", 14)
    pdf.drawString(100, 700, f"Name: {request.user.username}")
    pdf.drawString(100, 675, f"Test: {attempt.test.title}")
    pdf.drawString(100, 650, f"Score: {attempt.score}%")

    if attempt.end_time:
        pdf.drawString(100, 625, f"Date: {attempt.end_time.date()}")

    pdf.showPage()
    pdf.save()

    buffer.seek(0)

    response = HttpResponse(buffer, content_type="application/pdf")
    response["Content-Disposition"] = 'attachment; filename=\"certificate.pdf\"'
    return response


# -----------------------------
# USER DASHBOARD
# -----------------------------
@login_required
def user_dashboard(request):
    attempts = UserTestAttempt.objects.filter(user=request.user).order_by("-end_time")

    return render(request, "quizzes/user_dashboard.html", {
        "completed_attempts": attempts,
    })
