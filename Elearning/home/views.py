from django.shortcuts import render
from django.http import HttpResponse

def home(request):
    return render(request, 'home/index.html')

def cauhinhhethong(request):
    return render(request, 'Cauhinhhethong/cauhinhhethong.html')
def baomatvaquyenhan(request):
    return render(request, 'baomatvaquyenhan/baomatvaquyenhan.html')