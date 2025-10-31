# quizzes/models.py

from django.db import models
from django.contrib.auth import get_user_model 

User = get_user_model() 

# 1. The main Test/Quiz model
class Test(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
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
    # Make sure you have the MEDIA settings in settings.py for images to work
    image = models.ImageField(upload_to='question_images/', blank=True, null=True) 

    def __str__(self):
        return f"{self.test.title} - Question {self.id}"

# 3. The Answer Option model
class Answer(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='answers')
    text = models.CharField(max_length=500)
    is_correct = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.question.id}: {self.text[:30]}..."


# 4. Model to track a specific user's attempt at a test (NEW)
class UserTestAttempt(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    test = models.ForeignKey('Test', on_delete=models.CASCADE)
    start_time = models.DateTimeField(auto_now_add=True)
    end_time = models.DateTimeField(null=True, blank=True)
    score = models.IntegerField(null=True, blank=True)
    is_completed = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.user.username}'s attempt on {self.test.title}"

# 5. Model to record the user's answer to a single question (NEW)
class UserAnswer(models.Model):
    attempt = models.ForeignKey(UserTestAttempt, on_delete=models.CASCADE, related_name='answers')
    question = models.ForeignKey('Question', on_delete=models.CASCADE)
    selected_answer = models.ForeignKey('Answer', on_delete=models.SET_NULL, null=True, blank=True) 
    text_input = models.TextField(blank=True) 
    is_correct = models.BooleanField(default=False)

    def __str__(self):
        return f"Answer for Q{self.question.id} by {self.attempt.user.username}"