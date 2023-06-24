from django.shortcuts import render
from departments.models import Department
# Create your views here.

def mainPage(request):
    return render(request, 'main/home.html',{
        'depts': Department.objects.all()
    })