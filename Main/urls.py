from django.urls import path, include
from . import views


app_name = 'Main'

urlpatterns = [
    path('home/', views.mainPage, name='home'),
]