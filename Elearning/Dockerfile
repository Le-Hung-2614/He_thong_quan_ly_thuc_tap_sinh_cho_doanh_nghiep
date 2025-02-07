# Sử dụng Python slim làm base image
FROM python:3-slim

# Cập nhật package list và cài đặt thư viện cần thiết
RUN apt-get update && apt-get install -y \
    gcc \
    default-libmysqlclient-dev \
    pkg-config \
    && rm -rf /var/lib/apt/lists/*

# Thiết lập thư mục làm việc
WORKDIR /app

# Sao chép file requirements.txt vào container
COPY requirements.txt .

# Cài đặt các gói Python cần thiết
RUN python -m pip install --no-cache-dir -r requirements.txt

# Sao chép toàn bộ mã nguồn vào container
COPY . .

# Chạy server Django
CMD ["python", "Elearning/manage.py", "runserver", "0.0.0.0:9000"]
