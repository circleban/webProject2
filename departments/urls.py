from django.urls import path
from . import views


app_name = 'dept'

urlpatterns = [
    path('admin/<str:deptId>/', views.adminPage, name='admin'),
    path('<str:deptId>/', views.homePage, name='home'),
    path('<str:deptId>/login/', views.loginPage, name='login'),
    path('<str:deptId>/logout/', views.logoutPage, name='logout'),
    path('admin/<str:deptId>/add-course', views.addCourse, name='addCourse'),
    path('admin/<str:deptId>/modify-course/', views.modifyCourse, name='modifyCourse'),
    path('admin/<str:deptId>/add-teacher/', views.addTeacher, name='addTeacher'),
    path('admin/<str:deptId>/all-teachers/', views.allTeachers, name='allTeachers'),
    path('admin/<str:deptId>/semesters/', views.allSemesters, name='allSemesters'),
    path('admin/<str:deptId>/add-series/', views.addSeries, name='addSeries'),
    path('admin/<str:deptId>/modify-course/<int:semester_id>/', views.courseTable, name='courseTable'),
    path('admin/<str:deptId>/edit-course/<str:courseId>/', views.editCourse, name='editCourse'),
    path('admin/<str:deptId>/delete-course/<str:courseId>/', views.deleteCourse, name='deleteCourse'),
]