from django.urls import path
from . import views

app_name = 'teachers'

urlpatterns = [
    path('', views.home, name='home'),
    path('login/', views.loginTeacher, name='login'),
    path('register/', views.register, name='register'),
    path('logout/', views.logoutTeacher, name='logout'),
    path('teaches/', views.teaches, name='teaches'),
    path('teaches/<str:courseId>/', views.teaches_course, name='teaches_course'),
]