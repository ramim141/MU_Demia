from django.shortcuts import render

def home(request):
    return render(request, 'core/home.html')  # Make sure this path is correct