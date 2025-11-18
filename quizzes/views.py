# quizzes/views.py

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib import messages
from django.contrib.auth import login as auth_login
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.db.models import Q
import os
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.utils import ImageReader
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import Paragraph
from io import BytesIO
import qrcode
import base64
from .models import Test, Question, Answer, UserTestAttempt, UserAnswer
from django.conf import settings
import google.generativeai as genai
import requests
import math
from io import BytesIO
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.colors import HexColor
from django.utils import timezone  
import json
import random
from django.http import JsonResponse, HttpResponseBadRequest
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.utils import timezone
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
    # 5. AI FEEDBACK
    # ------------------------------
    ai_feedback = generate_ai_feedback(
        iq_score,
        category_results,
        correct_count,
        total_questions
    )

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
        "ai_feedback": ai_feedback,
    })




# -----------------------------
# DOWNLOAD CERTIFICATE (Premium PDF)
# -----------------------------
@login_required
def download_certificate(request, attempt_id):
    

    attempt = get_object_or_404(UserTestAttempt, pk=attempt_id)

    # CATEGORY IQ RESULTS (same logic as results page)
    questions = Question.objects.filter(test=attempt.test)
    user_answers = UserAnswer.objects.filter(attempt=attempt).select_related("selected_answer", "question")

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

        cat_ratio = correct_cat / total_cat
        cat_iq = int(60 + cat_ratio * 100)

        category_results.append((name, correct_cat, total_cat, cat_iq))

    # ----------------------- PDF START -----------------------
    buffer = BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4

    # Colors
    primary = colors.HexColor("#3B82F6")      # Blue
    dark = colors.HexColor("#0F172A")         # Dark blue-black
    gray_light = colors.HexColor("#94A3B8")   # Soft gray

    # ----------------------- BACKGROUND -----------------------
    # Light geometric brain watermark
    brain_path = os.path.join(settings.BASE_DIR, "static", "img", "brain.png")
    if os.path.exists(brain_path):
        pdf.drawImage(
            ImageReader(brain_path),
            80, 200,
            width=450, height=450,
            mask='auto',
            preserveAspectRatio=True,
            anchor='c'
        )

    # ----------------------- HEADER -----------------------
    pdf.setFillColor(primary)
    pdf.rect(0, height - 80, width, 80, fill=1)

    pdf.setFillColor(colors.white)
    pdf.setFont("Helvetica-Bold", 28)
    pdf.drawCentredString(width / 2, height - 45, "OFFICIAL IQ CERTIFICATE")

    # ----------------------- NAME -----------------------
    pdf.setFillColor(dark)
    pdf.setFont("Helvetica-Bold", 24)
    pdf.drawCentredString(width / 2, height - 140, attempt.user.username)

    pdf.setFont("Helvetica", 14)
    pdf.drawCentredString(width / 2, height - 165, f"has successfully completed")

    # ----------------------- TEST TITLE -----------------------
    pdf.setFont("Helvetica-Bold", 18)
    pdf.drawCentredString(width / 2, height - 195, attempt.test.title)

    # ----------------------- IQ SCORE BADGE -----------------------
    pdf.setFillColor(primary)
    pdf.circle(width / 2, height - 290, 55, fill=1)

    pdf.setFillColor(colors.white)
    pdf.setFont("Helvetica-Bold", 36)
    pdf.drawCentredString(width / 2, height - 300, str(int(attempt.iq_score)))

    pdf.setFont("Helvetica", 12)
    pdf.drawCentredString(width / 2, height - 325, "IQ SCORE")

    # ----------------------- CATEGORY TABLE -----------------------
    y = height - 420
    pdf.setFont("Helvetica-Bold", 16)
    pdf.setFillColor(dark)
    pdf.drawString(70, y, "Category Performance")
    y -= 30

    pdf.setFont("Helvetica-Bold", 12)
    pdf.setFillColor(primary)
    pdf.drawString(70, y, "Category")
    pdf.drawString(230, y, "Correct")
    pdf.drawString(330, y, "Total")
    pdf.drawString(430, y, "IQ")
    y -= 20

    pdf.setFillColor(dark)
    pdf.setFont("Helvetica", 12)

    for name, corr, tot, iq in category_results:
        pdf.drawString(70, y, name)
        pdf.drawString(230, y, str(corr))
        pdf.drawString(330, y, str(tot))
        pdf.drawString(430, y, str(iq))
        y -= 22

    # ----------------------- DATE -----------------------
    pdf.setFont("Helvetica", 12)
    pdf.setFillColor(gray_light)
    pdf.drawString(70, 120, f"Date: {attempt.end_time.date()}")

    # ----------------------- SIGNATURE -----------------------
    pdf.setFillColor(dark)
    pdf.setFont("Helvetica-Bold", 14)
    pdf.drawString(70, 90, "Certified by TestIQ Platform")

    pdf.line(70, 85, 250, 85)

    # ----------------------- QR CODE -----------------------
    qr_data = f"https://yourdomain.com/certificate/verify/{attempt.id}/"
    qr_img = qrcode.make(qr_data)
    qr_buffer = BytesIO()
    qr_img.save(qr_buffer, format="PNG")
    qr_buffer.seek(0)

    pdf.drawImage(ImageReader(qr_buffer), width - 150, 60, width=80, height=80)

    # ----------------------- FINALIZE -----------------------
    pdf.showPage()
    pdf.save()

    buffer.seek(0)
    return HttpResponse(buffer, content_type="application/pdf")



# -----------------------------
# USER DASHBOARD
# -----------------------------
@login_required
def user_dashboard(request):
    attempts = UserTestAttempt.objects.filter(user=request.user).order_by("-end_time")

    return render(request, "quizzes/user_dashboard.html", {
        "completed_attempts": attempts,
    })

def landing(request):
    print("LANDING VIEW WORKING")
    sample_questions = [
        ("sample_1.png", "Pattern Recognition", "Find the missing bar in the pattern."),
        ("sample_2.png", "Shape Sequence", "Identify Total no of cubes in image."),
        ("sample_3.png", "Pattern Recognition", "Find the missing bar in the pattern."),
        ("sample_4.png", "Directional Reasoning", "Predict the final arrow direction."),
    ]

    return render(request, "quizzes/landing.html", {
        "sample_questions": sample_questions
    })

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

def generate_ai_feedback(iq_score, category_results, correct_count, total_questions):
    categories_text = "\n".join(
        [f"{c['name']}: {c['correct']}/{c['total']} (IQ {c['iq']})"
         for c in category_results]
    )

    model = genai.GenerativeModel(
        "gemini-2.5-flash-lite",
        system_instruction=(
            "You are an expert psychometric evaluator. Your ONLY task is to generate "
            "personalized IQ feedback based on the user's test results. "
            "NEVER introduce yourself. NEVER ask what the user wants. "
            "NEVER provide general psychology help. Do not explain cognition topics. "
            "Respond ONLY with structured feedback: strengths, weaknesses, interpretation, "
            "and improvement plan. Keep length between 180 and 250 words."
        )
    )

    prompt = f"""
    Generate personalized IQ test feedback.

    User results:
    - IQ Score: {iq_score}
    - Correct Answers: {correct_count}/{total_questions}
    - Category Breakdown:
      {categories_text}

    Structure your feedback EXACTLY in this format:

    1. **Strengths** — based on performance.
    2. **Areas to Improve** — based strictly on weaker categories.
    3. **IQ Interpretation** — short explanation of what their IQ means.
    4. **Personalized Improvement Plan** — 3–5 bullet points.
    """

    response = model.generate_content(prompt)

    # Extract correctly for your SDK
    try:
        text = response.candidates[0].content.parts[0].text.strip()
        return text
    except Exception as e:
        print("AI EXTRACT ERROR:", e)
        return "⚠️ AI feedback could not be generated. Please try again."


def practice_home(request):
    return render(request, "quizzes/practice_home.html")


def sudoku_game(request):
    # Fetch puzzle from free API
    api_url = "https://sudoku-api.vercel.app/api/dosuku"
    puzzle = requests.get(api_url).json()

    grid = puzzle["newboard"]["grids"][0]["value"]  # 9x9 grid

    return render(request, "quizzes/sudoku.html", {
        "grid": grid
    })

# MEMORY GAME (render)
def memory_game(request):
    """
    Renders the memory match game. The board is generated in JS,
    so we just render the template. You can pass options if needed.
    """
    # You can tune board size here (pairs_count). Default: 8 pairs => 4x4 grid
    return render(request, "quizzes/memory_game.html", {"pairs_count": 8})


# MEMORY SCORE SAVE (AJAX) - optional persistence
@login_required
@require_POST
def save_memory_score(request):
    """
    Accepts JSON POST: {"moves": int, "time": seconds, "pairs": int}
    Saves score for the logged-in user if desired. Returns JSON result.
    """
    try:
        payload = json.loads(request.body.decode("utf-8"))
        moves = int(payload.get("moves", 0))
        time_taken = float(payload.get("time", 0))
        pairs = int(payload.get("pairs", 0))
    except Exception:
        return HttpResponseBadRequest("Invalid payload")

    # OPTIONAL: persist to DB if you have a model. For now, just echo back.
    score_data = {
        "user": request.user.username,
        "moves": moves,
        "time": time_taken,
        "pairs": pairs,
        "saved_at": timezone.now().isoformat()
    }

    # If you want to store in DB, uncomment and create a model GameScore.
    # GameScore.objects.create(user=request.user, game_name="memory", moves=moves, time_taken=time_taken, pairs=pairs)

    return JsonResponse({"status": "ok", "score": score_data})

def puzzle_game(request):
    # Fetch puzzle from PuzzleDB API
    api_url = "https://api.puzzlehub.org/v1/puzzles?type=logic&limit=1"
    try:
        response = requests.get(api_url, timeout=5).json()
        puzzle = response["puzzles"][0]
    except Exception:
        puzzle = {
            "question": "API error. Here's a backup puzzle: What comes next? 2, 4, 8, 16, ?",
            "answer": "32"
        }

    return render(request, "quizzes/puzzle_game.html", {
        "puzzle": puzzle
    })