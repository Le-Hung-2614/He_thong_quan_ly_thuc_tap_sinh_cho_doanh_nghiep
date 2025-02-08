from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from . import views

urlpatterns = [
    # Trang chủ
    path('', views.home, name='home'),
    
    # Nhóm chức năng đăng nhập, đăng ký, quên mật khẩu
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('forgot-password/', views.forgot_password_view, name='forgot_password'),
    path('logout/', views.logout_view, name='logout'),

    # Xác thực email và đặt lại mật khẩu
    path('activate/<uidb64>/<token>/', views.activate_account, name='activate_account'),
    path('reset-password/<uidb64>/<token>/', views.reset_password, name='reset_password'),

    # Nhóm chức năng quản lý
    path('quanlituyendung/', views.quanlituyendung, name='quanlituyendung'),
    path('lichphongvan/', views.lichphongvan, name='lichphongvan'),
    path('chuongtrinhdaotao/', views.chuongtrinhdaotao, name='chuongtrinhdaotao'),
    path('theodoihieusuat/', views.theodoihieusuat, name='theodoihieusuat'),
    path('giaotiepvaphanhoi/', views.giaotiepvaphanhoi, name='giaotiepvaphanhoi'),
    path('quanlyhoso/', views.quanlyhoso, name='quanlyhoso'),
    path('baocaovaphantich/', views.baocaovaphantich, name='baocaovaphantich'),
    path('cauhinhhethong/', views.cauhinhhethong, name='cauhinhhethong'),
    path('baomatvaquyenhan/', views.baomatvaquyenhan, name='baomatvaquyenhan'),
    path('create-recruitment/', views.create_recruitment, name='create_recruitment'),

    # Nhóm chức năng cá nhân
    path('myprofile/', views.myprofile, name='myprofile'),
    path('reports/', views.reports, name='reports'),
    path('helpvasupport/', views.helpvasupport, name='helpvasupport'),

    # Quản lý thông báo
    path('notifications/', views.notification_list, name='notification_list'),
    path('notifications/<int:pk>/mark-as-read/', views.mark_notification_as_read, name='mark_notification_as_read'),
    path('notifications/<int:pk>/delete/', views.delete_notification, name='delete_notification'),

    # Quản lý công việc
    path('tasks/', views.task_list, name='task_list'),
    path('tasks/<int:pk>/', views.task_detail, name='task_detail'),
    path('tasks/create/', views.task_create, name='task_create'),
    path('tasks/<int:pk>/update/', views.task_update, name='task_update'),
    path('tasks/<int:pk>/delete/', views.task_delete, name='task_delete'),

    # Quản lý ứng viên
    path('manage_candidates/', views.manage_candidates, name='manage_candidates'),
    path('schedule_interview/', views.schedule_interview, name='schedule_interview'),
    path('evaluate_candidate/<int:candidate_id>/', views.evaluate_candidate, name='evaluate_candidate'),

    # Quản lý phản hồi
    path('feedbacks/', views.feedback_list, name='feedback_list'),
    path('feedbacks/<int:pk>/', views.feedback_detail, name='feedback_detail'),
    path('feedbacks/create/', views.feedback_create, name='feedback_create'),

    # Quản lý hiệu suất
    path('performances/', views.performance_list, name='performance_list'),
    path('performances/<int:pk>/', views.performance_detail, name='performance_detail'),

    # Quản lý chương trình đào tạo
    path('training-programs/<int:pk>/enroll/', views.enroll_training_program, name='enroll_training_program'),

    # Quản lý hồ sơ cá nhân
    path('update-profile/', views.update_profile, name='update_profile'),

    # Quản lý điểm danh
    path('attendances/', views.attendance_list, name='attendance_list'),
    path('attendances/<int:pk>/', views.attendance_detail, name='attendance_detail'),
    path('attendances/create/', views.attendance_create, name='attendance_create'),
    path('attendances/<int:pk>/update/', views.attendance_update, name='attendance_update'),
    path('attendances/<int:pk>/delete/', views.attendance_delete, name='attendance_delete'),

    # Quản lý sự kiện
    path('events/', views.event_list, name='event_list'),
    path('events/<int:pk>/', views.event_detail, name='event_detail'),
    path('events/create/', views.event_create, name='event_create'),
    path('events/<int:pk>/update/', views.event_update, name='event_update'),
    path('events/<int:pk>/delete/', views.event_delete, name='event_delete'),
    path('quanlituyendung/tao-bai-dang/', views.create_job_post, name='create_job_post'),
    path('quanlituyendung/quan-ly-ung-vien/', views.manage_candidates, name='manage_candidates'),
    path('quanlituyendung/lich-phong-van/', views.schedule_interview, name='schedule_interview'),
    path('quanlituyendung/danh-gia-ung-vien/<int:candidate_id>/', views.evaluate_candidate, name='evaluate_candidate'),
    path('quanlituyendung/generate-report/', views.generate_report, name='generate_report'),
    path('quanlituyendung/integrate-system/', views.integrate_system, name='integrate_system'),
    path('quanlituyendung/manage-permissions/', views.manage_permissions, name='manage_permissions'),

    # Lịch phỏng vấn
    path('lichphongvan/', views.interview_list, name='lichphongvan'),
    path('lichphongvan/schedule/', views.schedule_interview, name='schedule_interview'),
    path('lichphongvan/edit/<int:pk>/', views.edit_interview, name='edit_interview'),
    path('lichphongvan/delete/<int:pk>/', views.delete_interview, name='delete_interview'),
]

# Phục vụ file media trong môi trường DEBUG
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)