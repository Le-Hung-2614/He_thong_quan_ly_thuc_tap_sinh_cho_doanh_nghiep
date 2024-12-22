from django.db import models

# Create your models here.
class cource(models. Model):
    cource_name = models. CharField (max_length=50)
    start_date = models. DateField()
    end_date = models. DateField()

class student(models. Model):
    name = models. CharField(max_length= 255)
# chua khai bao moi quan he ???