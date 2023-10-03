from django.urls import path, include
from . import views


app_name = 'Main'

urlpatterns = [
    path('home/', views.mainPage, name='home'),
    path('payment/', views.payment, name='payment'),
    path('payment/success/<str:id>', views.success, name='success'),
]