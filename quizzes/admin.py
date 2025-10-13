# quizzes/admin.py

from django.contrib import admin
from .models import Test, Question, Answer

# This makes the Answer model editable directly on the Question edit page
class AnswerInline(admin.TabularInline):
    model = Answer
    extra = 4  # Number of extra blank forms

@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    inlines = [AnswerInline]
    list_display = ('text', 'test', 'question_type')
    list_filter = ('test', 'question_type')

@admin.register(Test)
class TestAdmin(admin.ModelAdmin):
    list_display = ('title', 'duration', 'created_at')



