# quizzes/models.py

from django.db import models
from django.conf import settings
from django.contrib.auth import get_user_model # Use this for the User model

User = get_user_model() # Gets the active user model

# 1. The main Test/Quiz model
class Test(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    # Duration in minutes
    duration = models.IntegerField(default=30, help_text="Duration in minutes")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

# 2. The Question model
class Question(models.Model):
    TEST_TYPES = [
        ('MC', 'Multiple Choice'),
        ('VI', 'Visual/Image'),
        ('LG', 'Logic/Text Input'),
    ]

    test = models.ForeignKey(Test, on_delete=models.CASCADE, related_name='questions')
    text = models.TextField()
    question_type = models.CharField(max_length=2, choices=TEST_TYPES, default='MC')
    image = models.ImageField(upload_to='question_images/', blank=True, null=True)

    def __str__(self):
        return f"{self.test.title} - Question {self.id}"

# 3. The Answer Option model (for Multiple Choice)
class Answer(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='answers')
    text = models.CharField(max_length=500)
    is_correct = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.question.id}: {self.text[:30]}..."

 # 4. Model to record a user starting a test   
class UserTestAttempt(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    test = models.ForeignKey('Test', on_delete=models.CASCADE)
    start_time = models.DateTimeField(auto_now_add=True)
    end_time = models.DateTimeField(null=True, blank=True)
    score = models.IntegerField(null=True, blank=True)
    is_completed = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.user.username} - {self.test.title} ({'Completed' if self.is_completed else 'In Progress'})"

# 5. Model to record a user's answer for each question
class UserAnswer(models.Model):
    attempt = models.ForeignKey(UserTestAttempt, on_delete=models.CASCADE, related_name='answers')
    question = models.ForeignKey('Question', on_delete=models.CASCADE)
    # The user's selected answer (for MCQs) or text input (for logic questions)
    selected_answer = models.ForeignKey('Answer', on_delete=models.SET_NULL, null=True, blank=True) 
    text_input = models.TextField(blank=True) # For non-multiple choice questions
    is_correct = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.attempt.user.username}'s answer for Q{self.question.id}"