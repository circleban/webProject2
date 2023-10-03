from django.urls import path
from . import views

app_name = 'students'

urlpatterns = [
    path('', views.home, name='home'),
    path('login/', views.loginStudent, name='login'),
    path('logout/', views.logoutStudent, name='logout'),
    path('course-reg', views.courseReg, name='courseReg'),
]