from django.shortcuts import render
from django.http import HttpResponse

# Create your views here.
def index(request):
    return HttpResponse('This is app 1')
<<<<<<< HEAD

def index1(request):
    return HttpResponse('This is child 1')
=======
def index1(request):
    return HttpResponse('This is app 2')
>>>>>>> 1e2ef9fc9e3d3539620c61f682e9391d64602688
