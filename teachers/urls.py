from django.urls import path
from . import views

app_name = 'teachers'

urlpatterns = [
    path('', views.home, name='home'),
    path('login/', views.loginTeacher, name='login'),
    path('register/', views.register, name='register'),
    path('logout/', views.logoutTeacher, name='logout')
]