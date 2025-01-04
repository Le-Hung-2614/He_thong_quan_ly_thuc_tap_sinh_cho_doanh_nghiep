from django.db import models
from django.contrib.auth.models import User

class Intern(models.Model):
    # Thông tin cơ bản của thực tập sinh
    first_name = models.CharField(max_length=100, verbose_name="Tên")
    last_name = models.CharField(max_length=100, verbose_name="Họ")
    email = models.EmailField(unique=True, verbose_name="Email")
    phone = models.CharField(max_length=15, verbose_name="Số điện thoại")
    address = models.TextField(verbose_name="Địa chỉ")
    date_of_birth = models.DateField(verbose_name="Ngày sinh")
    university = models.CharField(max_length=200, verbose_name="Trường đại học")
    major = models.CharField(max_length=200, verbose_name="Chuyên ngành")
    start_date = models.DateField(verbose_name="Ngày bắt đầu thực tập")
    end_date = models.DateField(verbose_name="Ngày kết thúc thực tập")
    status = models.CharField(
        max_length=20,
        choices=[
            ('active', 'Đang thực tập'),
            ('completed', 'Đã hoàn thành'),
            ('terminated', 'Đã chấm dứt'),
        ],
        default='active',
        verbose_name="Trạng thái"
    )

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

class Recruitment(models.Model):
    # Thông tin tuyển dụng
    position = models.CharField(max_length=200, verbose_name="Vị trí tuyển dụng")
    description = models.TextField(verbose_name="Mô tả công việc")
    requirements = models.TextField(verbose_name="Yêu cầu")
    posted_by = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Người đăng")
    posted_date = models.DateTimeField(auto_now_add=True, verbose_name="Ngày đăng")
    deadline = models.DateField(verbose_name="Hạn nộp hồ sơ")

    def __str__(self):
        return self.position

class TrainingProgram(models.Model):
    # Chương trình đào tạo
    name = models.CharField(max_length=200, verbose_name="Tên chương trình")
    description = models.TextField(verbose_name="Mô tả")
    start_date = models.DateField(verbose_name="Ngày bắt đầu")
    end_date = models.DateField(verbose_name="Ngày kết thúc")
    trainer = models.CharField(max_length=200, verbose_name="Người đào tạo")
    interns = models.ManyToManyField(Intern, related_name='training_programs', verbose_name="Thực tập sinh")

    def __str__(self):
        return self.name

class Performance(models.Model):
    # Đánh giá hiệu suất
    intern = models.ForeignKey(Intern, on_delete=models.CASCADE, verbose_name="Thực tập sinh")
    evaluator = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Người đánh giá")
    evaluation_date = models.DateField(auto_now_add=True, verbose_name="Ngày đánh giá")
    score = models.DecimalField(max_digits=5, decimal_places=2, verbose_name="Điểm số")
    comments = models.TextField(verbose_name="Nhận xét")

    def __str__(self):
        return f"Đánh giá của {self.evaluator} cho {self.intern}"

class Feedback(models.Model):
    # Phản hồi từ thực tập sinh
    intern = models.ForeignKey(Intern, on_delete=models.CASCADE, verbose_name="Thực tập sinh")
    feedback_date = models.DateField(auto_now_add=True, verbose_name="Ngày phản hồi")
    content = models.TextField(verbose_name="Nội dung phản hồi")
    response = models.TextField(blank=True, null=True, verbose_name="Phản hồi từ quản lý")

    def __str__(self):
        return f"Phản hồi từ {self.intern}"