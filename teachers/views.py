from django.shortcuts import render
from django.http import HttpResponseRedirect, JsonResponse, HttpResponseForbidden
from django.urls import reverse
from .models import Teacher
from .forms import *
from django.contrib.auth.models import User
from departments.models import Department
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
import json


# Create your views here.


def home(request):
    if not request.user.is_authenticated:
        messages.error(request, 'Please login as a teacher first')
        return HttpResponseRedirect(reverse('teachers:login'))
    try:
        teacher = Teacher.objects.get(user=request.user)
        print(teacher)
    except Teacher.DoesNotExist:

        messages.error(request, 'Please login as a teacher')
        return HttpResponseRedirect(reverse('teachers:login'))

    return render(request, 'teachers/home.html')


def loginTeacher(request):
    form = loginForm(request.POST or None)
    if request.method == 'POST':
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(request, username=username, password=password)
            if user is not None:
                if not Teacher.objects.filter(user=user).exists():
                    messages.error(request, 'You are not a teacher')
                    return HttpResponseRedirect(reverse('teachers:login'))
                login(request, user)
                return HttpResponseRedirect(reverse('teachers:home'))

        form.add_error(None, 'Invalid Credentials')
        return render(request, 'teachers/login.html', {
            'form': form
        })
    return render(request, 'teachers/login.html', {
        'form': form
    })


def register(request):
    if 'register' not in request.session:
        request.session['register'] = False
    try:
        if request.method == 'POST':
            if request.headers.get('X-objective', None) == 'register':
                if not request.session['register']:
                    return HttpResponseForbidden()
                form = TeacherRegisterForm(request.POST)
                if form.is_valid():
                    form.save()
                    request.session['register'] = False
                    messages.success(request, 'You have successfully registered. Please Login')
                    return JsonResponse({'success': True})
                else:
                    messages.error(request, 'Please correct the errors below')
                    return render(request, 'teachers/register.html', {
                        'form': form,
                        'objective': 'register',
                    })
            else:
                form = verificationForm(request.POST)
                if form.is_valid():
                    code = form.cleaned_data.get('code')
                    dept_id = form.cleaned_data.get('dept_id')
                    teacher = Teacher.objects.get(code=code, dept=Department.objects.get(dept_id=dept_id))
                    if teacher.user is not None:
                        messages.info(request, 'You have already registered. Please Login')
                        return HttpResponseRedirect(reverse('teachers:login'))
                    request.session['register'] = True
                    
                    first_name = teacher.first_name
                    last_name = teacher.last_name
                    form = TeacherRegisterForm(initial={'username':f'{code}-{dept_id}','code': code, 'dept_id': dept_id, 'first_name': first_name, 'last_name': last_name})
                    return render(request, 'teachers/register.html', {
                        'form': form,
                        'objective': 'register',
                    })
                else:
                    return render(request, 'teachers/register.html', {
                        'form': form,
                        'objective': 'verify',
                    })
    except Teacher.DoesNotExist:
        pass

    if request.method == 'GET':
        return render(request, 'teachers/register.html', {
            'form': verificationForm(),
            'objective': 'verify',
        })

def logoutTeacher(request):
    request.session.flush()
    logout(request)
    return HttpResponseRedirect(reverse('Main:home'))