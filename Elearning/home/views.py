# home/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.models import User, Group
from django.core.mail import send_mail
from django.conf import settings
from django.core.signing import TimestampSigner, BadSignature
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from django.utils import timezone
from datetime import timedelta
from django.contrib.auth.password_validation import validate_password
import logging
from .models import Intern, TrainingProgram, Task, Notification, Performance, Feedback, Department, Project, Attendance, Report, Event,Recruitment,JobPost,Candidate,Interview,CandidateEvaluation,UserPermission,Integration,Report
from django import forms
from .utils import get_user_groups_context
from .forms import RecruitmentForm
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

logger = logging.getLogger(__name__)

# Hàm gửi email xác thực tài khoản
def send_activation_email(user, request):
    try:
        signer = TimestampSigner()
        token = signer.sign(user.email)
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        activation_link = f"http://{request.get_host()}/activate/{uid}/{token}/"
        
        subject = 'Kích hoạt tài khoản của bạn'
        message = f'Xin chào {user.username},\n\nVui lòng nhấp vào liên kết dưới đây để kích hoạt tài khoản của bạn:\n\n{activation_link}\n\nNếu bạn không yêu cầu điều này, vui lòng bỏ qua email này.'
        send_mail(subject, message, settings.EMAIL_HOST_USER, [user.email])
    except Exception as e:
        logger.error(f"Lỗi khi gửi email kích hoạt: {str(e)}")
        raise

# Hàm gửi email đặt lại mật khẩu
def send_password_reset_email(user, request):
    try:
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        token = default_token_generator.make_token(user)
        reset_link = f"http://{request.get_host()}/reset-password/{uid}/{token}/"
        
        subject = 'Yêu cầu đặt lại mật khẩu'
        message = f'Xin chào {user.username},\n\nBạn đã yêu cầu đặt lại mật khẩu. Vui lòng nhấp vào liên kết dưới đây để đặt lại mật khẩu:\n\n{reset_link}\n\nNếu bạn không yêu cầu điều này, vui lòng bỏ qua email này.'
        send_mail(subject, message, settings.EMAIL_HOST_USER, [user.email])
    except Exception as e:
        logger.error(f"Lỗi khi gửi email đặt lại mật khẩu: {str(e)}")
        raise

@login_required
def home(request):
    active_interns = Intern.objects.filter(is_active=True).count()
    training_programs = TrainingProgram.objects.count()
    completed_tasks = Task.objects.filter(status='completed').count()
    total_tasks = Task.objects.count()
    remaining_tasks = total_tasks - completed_tasks
    completion_rate = (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0
    latest_notifications = Notification.objects.all().order_by('-created_at')[:5]

    completed_training_programs = TrainingProgram.objects.filter(status='completed').count()
    remaining_training_programs = training_programs - completed_training_programs

    context = {
        'completed_training_programs': completed_training_programs,
        'remaining_training_programs': remaining_training_programs,
        'completed_tasks': completed_tasks,
        'remaining_tasks': remaining_tasks,
        'active_interns': active_interns,
        'training_programs': training_programs,
        'completion_rate': completion_rate,
        'latest_notifications': latest_notifications,
    }
    # Thêm thông tin nhóm người dùng vào context
    context.update(get_user_groups_context(request.user))
    return render(request, 'home/index.html', context)

# Kiểm tra xem người dùng có phải là HR không
def is_hr(user):
    return user.groups.filter(name='HR Managers').exists()

# Trang quản lý tuyển dụng (chỉ HR và Admin)
@user_passes_test(lambda u: is_hr(u) or u.is_superuser)
def quanlituyendung(request):
    if request.method == 'POST':
        form = RecruitmentForm(request.POST)
        if form.is_valid():
            recruitment = form.save(commit=False)
            recruitment.posted_by = request.user
            try:
                recruitment.full_clean()  # Kiểm tra validation trước khi lưu
                recruitment.save()
                messages.success(request, 'Chiến dịch tuyển dụng đã được tạo thành công.')
                return redirect('quanlituyendung')
            except ValidationError as e:
                # Hiển thị lỗi validation cho người dùng
                for field, errors in e.message_dict.items():
                    for error in errors:
                        messages.error(request, f"{field}: {error}")
    else:
        form = RecruitmentForm()

    # Phân trang danh sách tuyển dụng
    recruitments_list = Recruitment.objects.all().order_by('-posted_date')
    paginator = Paginator(recruitments_list, 10)  # Hiển thị 10 chiến dịch trên mỗi trang
    page_number = request.GET.get('page')  # Lấy số trang từ query parameter

    try:
        recruitments = paginator.page(page_number)
    except PageNotAnInteger:
        # Nếu page không phải là số nguyên, hiển thị trang đầu tiên
        recruitments = paginator.page(1)
    except EmptyPage:
        # Nếu page vượt quá số trang có sẵn, hiển thị trang cuối cùng
        recruitments = paginator.page(paginator.num_pages)

    context = get_user_groups_context(request.user)
    context['recruitments'] = recruitments
    context['form'] = form
    return render(request, 'Quanlituyendung/quanlituyendung.html', context)

# Trang lịch phỏng vấn (chỉ HR, Admin, và Internship Coordinators)
@user_passes_test(lambda u: is_hr(u) or u.groups.filter(name='Internship Coordinators').exists() or u.is_superuser)
def lichphongvan(request):
    context = get_user_groups_context(request.user)
    return render(request, 'Lichphongvan/lichphongvan.html', context)

# Trang chương trình đào tạo (chỉ HR, Admin, và Internship Coordinators)
@user_passes_test(lambda u: is_hr(u) or u.groups.filter(name='Internship Coordinators').exists() or u.is_superuser)
def chuongtrinhdaotao(request):
    context = get_user_groups_context(request.user)
    return render(request, 'Chuongtrinhdaotao/chuongtrinhdaotao.html', context)

# Trang theo dõi hiệu suất (chỉ HR, Admin, Mentors, và Internship Coordinators)
@user_passes_test(lambda u: is_hr(u) or u.groups.filter(name='Mentors').exists() or u.groups.filter(name='Internship Coordinators').exists() or u.is_superuser)
def theodoihieusuat(request):
    context = get_user_groups_context(request.user)
    return render(request, 'Theodoihieusuat/theodoihieusuat.html', context)

# Trang giao tiếp và phản hồi (Tất cả người dùng)
def giaotiepvaphanhoi(request):
    context = get_user_groups_context(request.user)
    return render(request, 'Giaotiepvaphanhoi/giaotiepvaphanhoi.html', context)

# Trang quản lý hồ sơ (chỉ HR, Admin, và Internship Coordinators)
@user_passes_test(lambda u: is_hr(u) or u.groups.filter(name='Internship Coordinators').exists() or u.is_superuser)
def quanlyhoso(request):
    context = get_user_groups_context(request.user)
    return render(request, 'Quanlyhoso/quanlyhoso.html', context)

# Trang báo cáo và phân tích (chỉ HR và Admin)
@user_passes_test(lambda u: is_hr(u) or u.is_superuser)
def baocaovaphantich(request):
    context = get_user_groups_context(request.user)
    return render(request, 'Baocaovaphantich/baocaovaphantich.html', context)

# Trang cấu hình hệ thống (chỉ admin)
@user_passes_test(lambda u: u.is_superuser)
def cauhinhhethong(request):
    context = get_user_groups_context(request.user)
    return render(request, 'Cauhinhhethong/cauhinhhethong.html', context)

# Trang bảo mật và quyền hạn (chỉ admin)
@user_passes_test(lambda u: u.is_superuser)
def baomatvaquyenhan(request):
    context = get_user_groups_context(request.user)
    return render(request, 'baomatvaquyenhan/baomatvaquyenhan.html', context)

# Trang hồ sơ cá nhân (yêu cầu đăng nhập)
@login_required
def myprofile(request):
    context = get_user_groups_context(request.user)
    return render(request, 'home/myprofile/myprofile.html', context)

# Trang báo cáo (yêu cầu đăng nhập)
@login_required
def reports(request):
    context = get_user_groups_context(request.user)
    return render(request, 'home/reports/reports.html', context)

# Trang hỗ trợ
def helpvasupport(request):
    context = get_user_groups_context(request.user)
    return render(request, 'home/HelpvaSupport/helpvasupport.html', context)

# Đăng xuất
def logout_view(request):
    logout(request)
    response = redirect('login')
    response.delete_cookie('sessionid')
    return response

# Đăng nhập
def login_view(request):
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        remember_me = request.POST.get('rememberMe')

        user = authenticate(request, username=username, password=password)
        if user is not None:
            if user.is_active:
                login(request, user)
                if remember_me:
                    request.session.set_expiry(30 * 24 * 60 * 60)
                else:
                    request.session.set_expiry(0)
                return redirect('home')
            else:
                messages.error(request, 'Tài khoản của bạn chưa được kích hoạt. Vui lòng kiểm tra email để kích hoạt.')
                return redirect('login')
        else:
            messages.error(request, 'Tên đăng nhập hoặc mật khẩu không đúng. Vui lòng thử lại.')
            return redirect('login')

    return render(request, 'home/login.html')

# Đăng ký
def register_view(request):
    if request.method == 'POST':
        full_name = request.POST.get('fullName')
        email = request.POST.get('email')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirmPassword')

        if password != confirm_password:
            messages.error(request, 'Mật khẩu không khớp. Vui lòng thử lại.')
            return redirect('register')

        try:
            validate_email(email)
        except ValidationError:
            messages.error(request, 'Email không hợp lệ. Vui lòng nhập email đúng định dạng.')
            return redirect('register')

        if User.objects.filter(email=email).exists():
            messages.error(request, 'Email đã tồn tại. Vui lòng sử dụng email khác.')
            return redirect('register')

        try:
            user = User.objects.create_user(username=email, email=email, password=password)
            user.first_name = full_name
            user.is_active = False
            user.save()
            send_activation_email(user, request)
            messages.success(request, 'Tài khoản đã được tạo thành công. Vui lòng kiểm tra email để kích hoạt.')
            return redirect('login')
        except Exception as e:
            messages.error(request, f'Lỗi khi tạo tài khoản: {str(e)}')
            return redirect('register')

    return render(request, 'home/register.html')

# Xác thực tài khoản
def activate_account(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
        signer = TimestampSigner()
        email = signer.unsign(token, max_age=86400)
        
        if user.email == email:
            user.is_active = True
            user.save()
            messages.success(request, 'Tài khoản của bạn đã được kích hoạt. Vui lòng đăng nhập.')
            return redirect('login')
        else:
            messages.error(request, 'Liên kết kích hoạt không hợp lệ.')
            return redirect('home')
    except (TypeError, ValueError, OverflowError, User.DoesNotExist, BadSignature, ValidationError):
        messages.error(request, 'Liên kết kích hoạt không hợp lệ hoặc đã hết hạn.')
        return redirect('home')

# Quên mật khẩu
def forgot_password_view(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        try:
            validate_email(email)
        except ValidationError:
            messages.error(request, 'Email không hợp lệ.')
            return redirect('forgot_password')

        try:
            user = User.objects.get(email=email)
            send_password_reset_email(user, request)
            messages.success(request, 'Hướng dẫn đặt lại mật khẩu đã được gửi đến email của bạn.')
            return redirect('login')
        except User.DoesNotExist:
            messages.error(request, 'Không tìm thấy người dùng với email này.')
    
    return render(request, 'home/forgot_password.html')

# Đặt lại mật khẩu
def reset_password(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
        
        if default_token_generator.check_token(user, token):
            if request.method == 'POST':
                password = request.POST.get('password')
                confirm_password = request.POST.get('confirmPassword')
                
                if password == confirm_password:
                    try:
                        validate_password(password, user)
                        user.set_password(password)
                        user.save()
                        messages.success(request, 'Mật khẩu của bạn đã được đặt lại. Vui lòng đăng nhập.')
                        return redirect('login')
                    except ValidationError as e:
                        messages.error(request, f'Mật khẩu không hợp lệ: {", ".join(e.messages)}')
                else:
                    messages.error(request, 'Mật khẩu không khớp.')
            return render(request, 'home/reset_password.html')
        else:
            messages.error(request, 'Liên kết đặt lại mật khẩu không hợp lệ.')
            return redirect('home')
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        messages.error(request, 'Liên kết đặt lại mật khẩu không hợp lệ.')
        return redirect('home')

# Quản lý thông báo
@login_required
def notification_list(request):
    notifications = Notification.objects.filter(user=request.user).order_by('-created_at')
    context = get_user_groups_context(request.user)
    context['notifications'] = notifications
    return render(request, 'home/notification_list.html', context)

@login_required
def mark_notification_as_read(request, pk):
    notification = get_object_or_404(Notification, pk=pk, user=request.user)
    notification.is_read = True
    notification.save()
    return redirect('notification_list')

@login_required
def delete_notification(request, pk):
    notification = get_object_or_404(Notification, pk=pk, user=request.user)
    notification.delete()
    return redirect('notification_list')

# Quản lý công việc
@login_required
def task_list(request):
    tasks = Task.objects.filter(assigned_to=request.user).order_by('-created_at')
    context = get_user_groups_context(request.user)
    context['tasks'] = tasks
    return render(request, 'home/task_list.html', context)

@login_required
def task_detail(request, pk):
    task = get_object_or_404(Task, pk=pk, assigned_to=request.user)
    context = get_user_groups_context(request.user)
    context['task'] = task
    return render(request, 'home/task_detail.html', context)

@login_required
def task_create(request):
    class TaskForm(forms.Form):  # Tạo form trực tiếp trong view
        title = forms.CharField(max_length=255)
        description = forms.CharField(widget=forms.Textarea)
        status = forms.ChoiceField(choices=[('pending', 'Pending'), ('in_progress', 'In Progress'), ('completed', 'Completed')])
        priority = forms.ChoiceField(choices=[('low', 'Low'), ('medium', 'Medium'), ('high', 'High')])

    if request.method == 'POST':
        form = TaskForm(request.POST)
        if form.is_valid():
            title = form.cleaned_data['title']
            description = form.cleaned_data['description']
            status = form.cleaned_data['status']
            priority = form.cleaned_data['priority']
            Task.objects.create(
                title=title,
                description=description,
                status=status,
                priority=priority,
                assigned_to=request.user
            )
            messages.success(request, 'Công việc đã được tạo thành công.')
            return redirect('task_list')
    else:
        form = TaskForm()
    context = get_user_groups_context(request.user)
    context['form'] = form
    return render(request, 'home/task_form.html', context)

@login_required
def task_update(request, pk):
    task = get_object_or_404(Task, pk=pk, assigned_to=request.user)
    class TaskForm(forms.Form):  # Tạo form trực tiếp trong view
        title = forms.CharField(max_length=255, initial=task.title)
        description = forms.CharField(widget=forms.Textarea, initial=task.description)
        status = forms.ChoiceField(choices=[('pending', 'Pending'), ('in_progress', 'In Progress'), ('completed', 'Completed')], initial=task.status)
        priority = forms.ChoiceField(choices=[('low', 'Low'), ('medium', 'Medium'), ('high', 'High')], initial=task.priority)

    if request.method == 'POST':
        form = TaskForm(request.POST)
        if form.is_valid():
            task.title = form.cleaned_data['title']
            task.description = form.cleaned_data['description']
            task.status = form.cleaned_data['status']
            task.priority = form.cleaned_data['priority']
            task.save()
            messages.success(request, 'Công việc đã được cập nhật thành công.')
            return redirect('task_list')
    else:
        form = TaskForm()
    context = get_user_groups_context(request.user)
    context['form'] = form
    return render(request, 'home/task_form.html', context)

@login_required
def task_delete(request, pk):
    task = get_object_or_404(Task, pk=pk, assigned_to=request.user)
    task.delete()
    messages.success(request, 'Công việc đã được xóa thành công.')
    return redirect('task_list')

# Quản lý phản hồi
@login_required
def feedback_list(request):
    feedbacks = Feedback.objects.filter(intern__user=request.user).order_by('-feedback_date')
    context = get_user_groups_context(request.user)
    context['feedbacks'] = feedbacks
    return render(request, 'home/feedback_list.html', context)

@login_required
def feedback_detail(request, pk):
    feedback = get_object_or_404(Feedback, pk=pk, intern__user=request.user)
    context = get_user_groups_context(request.user)
    context['feedback'] = feedback
    return render(request, 'home/feedback_detail.html', context)

@login_required
def feedback_create(request):
    class FeedbackForm(forms.Form):  # Tạo form trực tiếp trong view
        content = forms.CharField(widget=forms.Textarea)

    if request.method == 'POST':
        form = FeedbackForm(request.POST)
        if form.is_valid():
            content = form.cleaned_data['content']
            Feedback.objects.create(
                content=content,
                intern=Intern.objects.get(user=request.user)
            )
            messages.success(request, 'Phản hồi của bạn đã được gửi thành công.')
            return redirect('feedback_list')
    else:
        form = FeedbackForm()
    context = get_user_groups_context(request.user)
    context['form'] = form
    return render(request, 'home/feedback_form.html', context)

# Quản lý hồ sơ cá nhân
@login_required
def update_profile(request):
    intern = Intern.objects.get(user=request.user)
    class InternForm(forms.Form):  # Tạo form trực tiếp trong view
        first_name = forms.CharField(max_length=100, initial=intern.first_name)
        last_name = forms.CharField(max_length=100, initial=intern.last_name)
        email = forms.EmailField(initial=intern.email)
        phone = forms.CharField(max_length=15, initial=intern.phone)
        address = forms.CharField(widget=forms.Textarea, initial=intern.address)
        date_of_birth = forms.DateField(initial=intern.date_of_birth)
        university = forms.CharField(max_length=200, initial=intern.university)
        major = forms.CharField(max_length=200, initial=intern.major)
        avatar = forms.ImageField(required=False)

    if request.method == 'POST':
        form = InternForm(request.POST, request.FILES)
        if form.is_valid():
            intern.first_name = form.cleaned_data['first_name']
            intern.last_name = form.cleaned_data['last_name']
            intern.email = form.cleaned_data['email']
            intern.phone = form.cleaned_data['phone']
            intern.address = form.cleaned_data['address']
            intern.date_of_birth = form.cleaned_data['date_of_birth']
            intern.university = form.cleaned_data['university']
            intern.major = form.cleaned_data['major']
            if form.cleaned_data['avatar']:
                intern.avatar = form.cleaned_data['avatar']
            intern.save()
            messages.success(request, 'Hồ sơ của bạn đã được cập nhật thành công.')
            return redirect('myprofile')
    else:
        form = InternForm()
    context = get_user_groups_context(request.user)
    context['form'] = form
    return render(request, 'home/update_profile.html', context)

@login_required
def view_badges(request):
    context = get_user_groups_context(request.user)
    return render(request, 'home/view_badges.html', context)

@login_required
def start_remaining_tasks(request):
    remaining_tasks = Task.objects.exclude(status='completed')
    context = get_user_groups_context(request.user)
    context['remaining_tasks'] = remaining_tasks
    return render(request, 'home/start_remaining_tasks.html', context)

# Quản lý điểm danh
@login_required
def attendance_list(request):
    attendances = Attendance.objects.all()
    context = get_user_groups_context(request.user)
    context['attendances'] = attendances
    return render(request, 'home/attendance_list.html', context)

@login_required
def attendance_detail(request, pk):
    attendance = get_object_or_404(Attendance, pk=pk)
    context = get_user_groups_context(request.user)
    context['attendance'] = attendance
    return render(request, 'home/attendance_detail.html', context)

# Quản lý điểm danh
@login_required
def attendance_create(request):
    context = get_user_groups_context(request.user)  # Khởi tạo context

    if request.method == 'POST':
        # Xử lý form tạo mới điểm danh
        pass
    else:
        # Hiển thị form tạo mới
        pass
    return render(request, 'home/attendance_form.html', context)

@login_required
def attendance_update(request, pk):
    attendance = get_object_or_404(Attendance, pk=pk)
    context = get_user_groups_context(request.user)  # Khởi tạo context
    context['attendance'] = attendance  # Thêm thông tin điểm danh vào context

    if request.method == 'POST':
        # Xử lý form cập nhật điểm danh
        pass
    else:
        # Hiển thị form cập nhật
        pass
    return render(request, 'home/attendance_form.html', context)

@login_required
def attendance_delete(request, pk):
    attendance = get_object_or_404(Attendance, pk=pk)
    attendance.delete()
    messages.success(request, 'Điểm danh đã được xóa thành công.')
    return redirect('attendance_list')

# Quản lý sự kiện
@login_required
def event_list(request):
    events = Event.objects.all()
    context = get_user_groups_context(request.user)
    context['events'] = events
    return render(request, 'home/event_list.html', context)

@login_required
def event_detail(request, pk):
    event = get_object_or_404(Event, pk=pk)
    context = get_user_groups_context(request.user)
    context['event'] = event
    return render(request, 'home/event_detail.html', context)

# Quản lý sự kiện
@login_required
def event_create(request):
    context = get_user_groups_context(request.user)  # Khởi tạo context

    if request.method == 'POST':
        # Xử lý form tạo mới sự kiện
        pass
    else:
        # Hiển thị form tạo mới
        pass
    return render(request, 'home/event_form.html', context)

@login_required
def event_update(request, pk):
    event = get_object_or_404(Event, pk=pk)
    context = get_user_groups_context(request.user)  # Khởi tạo context
    context['event'] = event  # Thêm thông tin sự kiện vào context

    if request.method == 'POST':
        # Xử lý form cập nhật sự kiện
        pass
    else:
        # Hiển thị form cập nhật
        pass
    return render(request, 'home/event_form.html', context)

@login_required
def event_delete(request, pk):
    event = get_object_or_404(Event, pk=pk)
    event.delete()
    messages.success(request, 'Sự kiện đã được xóa thành công.')
    return redirect('event_list')

# Quản lý báo cáo
@login_required
def report_list(request):
    reports = Report.objects.filter(user=request.user)
    context = get_user_groups_context(request.user)
    context['reports'] = reports
    return render(request, 'home/report_list.html', context)

@login_required
def report_detail(request, pk):
    report = get_object_or_404(Report, pk=pk, user=request.user)
    context = get_user_groups_context(request.user)
    context['report'] = report
    return render(request, 'home/report_detail.html', context)

# Quản lý hiệu suất
@login_required
def performance_list(request):
    performances = Performance.objects.filter(intern__user=request.user).order_by('-evaluation_date')
    context = get_user_groups_context(request.user)
    context['performances'] = performances
    return render(request, 'home/performance_list.html', context)

@login_required
def performance_detail(request, pk):
    performance = get_object_or_404(Performance, pk=pk, intern__user=request.user)
    context = get_user_groups_context(request.user)
    context['performance'] = performance
    return render(request, 'home/performance_detail.html', context)

@login_required
def enroll_training_program(request, pk):
    program = get_object_or_404(TrainingProgram, pk=pk)

@user_passes_test(lambda u: is_hr(u) or u.is_superuser)
def edit_recruitment(request, pk):
    recruitment = get_object_or_404(Recruitment, pk=pk)
    if request.method == 'POST':
        form = RecruitmentForm(request.POST, instance=recruitment)
        if form.is_valid():
            form.save()
            messages.success(request, 'Chiến dịch tuyển dụng đã được cập nhật.')
            return redirect('quanlituyendung')
    else:
        form = RecruitmentForm(instance=recruitment)
    
    context = get_user_groups_context(request.user)
    context['form'] = form
    return render(request, 'Quanlituyendung/edit_recruitment.html', context)

@user_passes_test(lambda u: is_hr(u) or u.is_superuser)
def delete_recruitment(request, pk):
    recruitment = get_object_or_404(Recruitment, pk=pk)
    recruitment.delete()
    messages.success(request, 'Chiến dịch tuyển dụng đã được xóa.')
    return redirect('quanlituyendung')

@login_required
def create_job_post(request):
    if request.method == 'POST':
        title = request.POST.get('jobPostTitle')
        description = request.POST.get('jobPostDescription')
        platform = request.POST.get('jobPostPlatform')

        # Kiểm tra xem các trường bắt buộc có được điền hay không
        if not title:
            messages.error(request, 'Tiêu đề không được để trống.')
            return redirect('quanlituyendung')
        if not platform:
            messages.error(request, 'Nền tảng không được để trống.')
            return redirect('quanlituyendung')

        # Tạo JobPost và lưu vào cơ sở dữ liệu
        try:
            JobPost.objects.create(
                title=title,
                description=description,
                platform=platform,
                posted_by=request.user
            )
            messages.success(request, 'Bài đăng tuyển dụng đã được tạo thành công.')
        except Exception as e:
            messages.error(request, f'Lỗi khi tạo bài đăng: {str(e)}')

        return redirect('quanlituyendung')
    
@login_required
def manage_candidates(request):
    candidates = Candidate.objects.all()
    context = {
        'candidates': candidates,
    }
    return render(request, 'quanlituyendung.html', context)

@login_required
def schedule_interview(request):
    if request.method == 'POST':
        candidate_id = request.POST.get('interviewCandidate')
        interview_date = request.POST.get('interviewDate')
        interview_time = request.POST.get('interviewTime')
        candidate = Candidate.objects.get(id=candidate_id)
        Interview.objects.create(
            candidate=candidate,
            interview_date=interview_date,
            interview_time=interview_time,
            interviewer=request.user
        )
        messages.success(request, 'Lịch phỏng vấn đã được tạo thành công.')
        return redirect('quanlituyendung')

@login_required
def evaluate_candidate(request):
    if request.method == 'POST':
        candidate_id = request.POST.get('candidateEvaluation')
        score = request.POST.get('evaluationScore')
        comments = request.POST.get('candidateEvaluation')
        candidate = Candidate.objects.get(id=candidate_id)
        CandidateEvaluation.objects.create(
            candidate=candidate,
            evaluator=request.user,
            score=score,
            comments=comments
        )
        messages.success(request, 'Đánh giá đã được lưu thành công.')
        return redirect('quanlituyendung')
    
@login_required
def generate_report(request):
    if request.method == 'POST':
        report_type = request.POST.get('reportType')
        content = request.POST.get('reportContent')
        Report.objects.create(
            report_type=report_type,
            generated_by=request.user,
            content=content
        )
        messages.success(request, 'Báo cáo đã được tạo thành công.')
        return redirect('quanlituyendung')
    
@login_required
def integrate_system(request):
    if request.method == 'POST':
        system = request.POST.get('integrationSystem')
        Integration.objects.create(
            system=system,
            integrated_by=request.user
        )
        messages.success(request, 'Hệ thống đã được tích hợp thành công.')
        return redirect('quanlituyendung')
    
@login_required
def manage_permissions(request):
    if request.method == 'POST':
        user_id = request.POST.get('userRole')
        role = request.POST.get('userRole')
        permission = request.POST.get('userPermissions')
        try:
            user = User.objects.get(id=user_id)
            group, created = Group.objects.get_or_create(name=role)
            user.groups.add(group)
            messages.success(request, f'Quyền truy cập của {user.username} đã được cập nhật thành công.')
        except User.DoesNotExist:
            messages.error(request, 'Người dùng không tồn tại.')
        return redirect('quanlituyendung')  # Chuyển hướng về trang quản lý tuyển dụng
    return render(request, 'manage_permissions.html')  # Hiển thị form quản lý quyền truy cập