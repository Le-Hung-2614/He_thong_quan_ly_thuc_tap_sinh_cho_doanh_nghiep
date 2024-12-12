from django.contrib import admin
from django.urls import path
<<<<<<< HEAD
from . import views 

urlpatterns = [
    path('', views.index),
    path('/1', views.index1)
=======
from . import views
urlpatterns = [
    path('',views.index),
    path('/1',views.index1)
>>>>>>> 1e2ef9fc9e3d3539620c61f682e9391d64602688
]