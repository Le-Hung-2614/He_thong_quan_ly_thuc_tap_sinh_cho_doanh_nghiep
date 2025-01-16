from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.models import User
from django.core.mail import send_mail  # Sửa lỗi chính tả ở đây
from django.conf import settings

def home(request):
    return render(request, 'home/index.html')

def cauhinhhethong(request):
    return render(request, 'Cauhinhhethong/cauhinhhethong.html')

def baomatvaquyenhan(request):
    return render(request, 'baomatvaquyenhan/baomatvaquyenhan.html')

def logout_view(request):  
    logout(request)
    return redirect('login')

def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, 'Invalid username or password.')
    return render(request, 'home/login.html')

def register_view(request):
    if request.method == 'POST':
        full_name = request.POST['fullName']
        email = request.POST['email']
        password = request.POST['password']
        confirm_password = request.POST['confirmPassword']

        if password != confirm_password:
            messages.error(request, 'Passwords do not match.')
            return redirect('register')

        try:
            user = User.objects.create_user(username=email, email=email, password=password)
            user.first_name = full_name
            user.save()
            messages.success(request, 'Account created successfully. Please login.')
            return redirect('login')
        except Exception as e:
            messages.error(request, 'Error creating account. Please try again.')
            return redirect('register')

    return render(request, 'home/register.html')

def forgot_password_view(request):
    if request.method == 'POST':
        email = request.POST['email']
        try:
            user = User.objects.get(email=email)
            # Gửi email đặt lại mật khẩu (ví dụ đơn giản)
            subject = 'Password Reset Request'
            message = f'Hi {user.username},\n\nYou requested a password reset. Please click the link below to reset your password:\n\nhttp://yourdomain.com/reset-password/\n\nIf you did not request this, please ignore this email.'
            send_mail(subject, message, settings.EMAIL_HOST_USER, [user.email])
            messages.success(request, 'Password reset instructions have been sent to your email.')
            return redirect('login')
        except User.DoesNotExist:
            messages.error(request, 'No user found with this email address.')
    return render(request, 'home/forgot_password.html')