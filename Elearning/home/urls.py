from django.contrib import admin
from django.urls import path, include
from . import views

urlpatterns = [
    path('', views.home, name="home"),
    path('cauhinhhethong/', views.cauhinhhethong, name='cauhinhhethong'),
    path('baomatvaquyenhan/', views.baomatvaquyenhan, name='baomatvaquyenhan'),
    path('logout/', views.logout_view, name='logout'),  # Sửa thành logout_view
    path('login/', views.login_view, name='login'),  
    path('register/', views.register_view, name='register'),  
    path('forgot-password/', views.forgot_password_view, name='forgot_password'),
]