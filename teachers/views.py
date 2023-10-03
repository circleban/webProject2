from django.shortcuts import render
from django.http import HttpResponseRedirect, JsonResponse, HttpResponseForbidden
from django.urls import reverse
from .models import Teacher
from departments.models import Course, Series, Department
from students.models import *
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

def teaches(request):
    try:
        teacher = Teacher.objects.get(user=request.user)
        courses = teacher.teaches.all()
        return render(request, 'teachers/teaches.html',
                    {
                        'courses': courses,
                    })
    except Teacher.DoesNotExist:
        messages.error(request, 'Please login as a teacher first')
        return HttpResponseRedirect(reverse('teachers:login'))

def teaches_course(request, courseId):
    try:
        teacher = Teacher.objects.get(user=request.user)
        course = Course.objects.get(title=courseId)
        if not teacher.teaches.filter(course=course).exists():
            return HttpResponseForbidden("You are not allowed to access this page")
        students = course.taken_by.filter(registraion='R')
        if request.method == "POST":
            return update_marks(request, teacher, course, students)
     
        context = {}
        no_of_cts = 0
        for sc in students:
            if sc.class_tests.all().exists():
                cts = sc.class_tests.all()
                no_of_cts = max(no_of_cts, len(cts))
            else:
                cts = None
            try:
                lab = sc.students_labcourse_exams.latest('id')
            except LabCourse.DoesNotExist:
                lab = None
            try:
                theory = sc.students_theorycourse_exams.latest('id')
            except TheoryCourse.DoesNotExist:
                theory = None
            context[sc.student.roll] = {
                'student': sc.student,
                'class_tests': cts,
                'lab': lab,
                'theory': theory,
                'theory_total': (theory.sectionA or 0) + (theory.sectionB or 0)+ (theory.attendance or 0) if theory else None,
                'lab_total': (lab.viva or 0) + (lab.labPerformance or 0) + (lab.labReport or 0) + (lab.attendance or 0) + (lab.labquiz or 0) + (lab.labfinal or 0) if lab else None,
            }
        # print(context, f'no_of_cts={no_of_cts}')
        return render(request, 'teachers/teaches_course.html',
                    {
                        'course': course,
                        'info': context,
                        'no_of_cts': range(1,no_of_cts+1),
                    })
    except Teacher.DoesNotExist:
        messages.error(request, 'Please login as a teacher first')
        return HttpResponseRedirect(reverse('teachers:login'))
    except Course.DoesNotExist:
        messages.error(request, 'Course not found')
        return HttpResponseRedirect(reverse('teachers:teaches'))
    except Series.DoesNotExist:
        return HttpResponseForbidden("You are not allowed to access this page")
    
def update_marks(request, teacher, course, students):
    print('In update marks')
    if request.POST.get('save-marks') == 'CT' and course.isTheoryCourse():
        for s in students:
            l = request.POST.getlist(f'{s.student.roll}-CT')
            cts = list(s.class_tests.all())
            for i in range(len(l)):
                try:
                    mark = int(l[i])
                except ValueError:
                    mark = None
                try:
                    if cts[i].obtained_marks is None and mark is not None:
                        print('In none')
                        cts[i].obtained_marks = mark
                        cts[i].taken_by = teacher
                        cts[i].save()
                    elif cts[i].taken_by == teacher:
                        print('In taken by')
                        cts[int(i)].obtained_marks = mark
                        cts[i].save()
                except IndexError:
                    ClassTest.objects.create(obtained_marks=mark, taken_by=teacher, ct_for=s)
                
    elif request.POST.get('save-marks') == 'lab' and not course.isTheoryCourse():
        print('In lab')
        for s in students:
            try:
                lab = s.students_labcourse_exams.latest('id')
            except LabCourse.DoesNotExist:
                messages.error(request, 'Lab exam not found')
                return HttpResponseRedirect(reverse('teachers:teaches_course', kwargs={'courseId': course.title}))
            
            try:
                print(f'Viva: {int(request.POST.get(f"{s.student.roll}-lab-viva"))}')
                lab.viva = int(request.POST.get(f'{s.student.roll}-lab-viva'))
            except ValueError:
                lab.viva = None
            try:
                print(f'labPerformance: {int(request.POST.get(f"{s.student.roll}-lab-perform"))}')
                lab.labPerformance = int(request.POST.get(f'{s.student.roll}-lab-perform'))
            except ValueError:
                lab.labPerformance = None
            try:
                print(f'labReport: {int(request.POST.get(f"{s.student.roll}-lab-report"))}')
                lab.labReport = int(request.POST.get(f'{s.student.roll}-lab-report'))
            except ValueError:
                lab.labReport = None
            try:
                print(f'labAttendance: {int(request.POST.get(f"{s.student.roll}-lab-attendance"))}')
                lab.attendance = int(request.POST.get(f'{s.student.roll}-lab-attendance'))
            except ValueError:
                lab.attendance = None
            try:
                print(f'labQuiz: {int(request.POST.get(f"{s.student.roll}-lab-quiz"))}')
                lab.labquiz = int(request.POST.get(f'{s.student.roll}-lab-quiz'))
            except ValueError:
                lab.labquiz = None
            try:
                print(f'labFinal: {int(request.POST.get(f"{s.student.roll}-lab-final"))}')
                lab.labfinal = int(request.POST.get(f'{s.student.roll}-lab-final'))
            except ValueError:
                lab.labfinal = None
                          
            lab.save()
    elif request.POST.get('save-marks') == 'semester-final' and course.isTheoryCourse():
        for s in students:
            try:
                theory = s.students_theorycourse_exams.latest('id')
            except TheoryCourse.DoesNotExist:
                messages.error(request, 'Theory exam not found')
                return HttpResponseRedirect(reverse('teachers:teaches_course', kwargs={'courseId': course.title}))
            
            try:
                print(f'sectionA: {int(request.POST.get(f"{s.student.roll}-sectionA"))}')
                theory.sectionA = int(request.POST.get(f'{s.student.roll}-sectionA'))
            except ValueError:
                theory.sectionA = None
            try:
                print(f'sectionB: {int(request.POST.get(f"{s.student.roll}-sectionB"))}')
                theory.sectionB = int(request.POST.get(f'{s.student.roll}-sectionB'))
            except ValueError:
                theory.sectionB = None
            try:
                print(f'attendance: {int(request.POST.get(f"{s.student.roll}-attendance"))}')
                theory.attendance = int(request.POST.get(f'{s.student.roll}-attendance'))
            except ValueError:
                theory.attendance = None
            theory.save()
    return HttpResponseRedirect(reverse('teachers:teaches_course', kwargs={'courseId': course.title}))

