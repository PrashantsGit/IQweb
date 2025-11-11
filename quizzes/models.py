from django.db import models
from django.contrib.auth.models import User

DIFFICULTY_LEVELS = [
    ('E', 'Easy'),
    ('M', 'Medium'),
    ('H', 'Hard'),
]

CATEGORY_CHOICES = [
    ('VR', 'Verbal Reasoning'),
    ('NR', 'Numerical Reasoning'),
    ('LR', 'Logical Reasoning'),
    ('SR', 'Spatial Reasoning'),
    ('MR', 'Memory'),
]


class Test(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    duration = models.IntegerField(help_text="Duration in minutes")

    def __str__(self):
        return self.title


class Question(models.Model):
    test = models.ForeignKey(Test, on_delete=models.CASCADE)
    text = models.TextField()
    image = models.ImageField(upload_to='questions/', blank=True, null=True)
    question_type = models.CharField(max_length=10, default='MC')
    category = models.CharField(max_length=2, choices=CATEGORY_CHOICES, default='LR')
    difficulty = models.CharField(max_length=1, choices=DIFFICULTY_LEVELS, default='M')

    def __str__(self):
        return self.text[:80]


class Answer(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    text = models.CharField(max_length=255)
    is_correct = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.text} ({'✔' if self.is_correct else '✖'})"


class UserTestAttempt(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    test = models.ForeignKey(Test, on_delete=models.CASCADE)
    start_time = models.DateTimeField(auto_now_add=True)
    end_time = models.DateTimeField(null=True, blank=True)
    is_completed = models.BooleanField(default=False)
    score = models.FloatField(default=0)
    iq_score = models.FloatField(default=0)

    def __str__(self):
        return f"{self.user.username} - {self.test.title}"


class UserAnswer(models.Model):
    attempt = models.ForeignKey(UserTestAttempt, on_delete=models.CASCADE)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    selected_answer = models.ForeignKey(Answer, on_delete=models.CASCADE, null=True, blank=True)
    text_input = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.attempt.user.username} - {self.question.text[:40]}"
