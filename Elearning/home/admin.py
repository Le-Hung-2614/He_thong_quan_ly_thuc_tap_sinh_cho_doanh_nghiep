from django.contrib import admin
from .models import Intern, Recruitment, TrainingProgram, Performance, Feedback

# Đăng ký các model
admin.site.register(Intern)
admin.site.register(Recruitment)
admin.site.register(TrainingProgram)
admin.site.register(Performance)
admin.site.register(Feedback)