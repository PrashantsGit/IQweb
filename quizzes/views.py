from django.shortcuts import render
from .models import Test

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