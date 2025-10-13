# quizzes/models.py

from django.db import models
from django.conf import settings

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