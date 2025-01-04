from django.shortcuts import render
from django.http import response
# Create your views here.

def home(request):
    return render(request, 'home/index.html')