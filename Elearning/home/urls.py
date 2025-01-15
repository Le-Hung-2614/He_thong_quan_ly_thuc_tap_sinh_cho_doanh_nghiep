from django.contrib import admin
from django.urls import path,include
from .import views 

urlpatterns = [
    path('', views.home, name="home"),
    path('cauhinhhethong/', views.cauhinhhethong, name='cauhinhhethong'),
    path('baomatvaquyenhan/', views.baomatvaquyenhan, name='baomatvaquyenhan'),
]
