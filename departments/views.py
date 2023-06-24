from django.shortcuts import render
from django.http import HttpResponseRedirect, JsonResponse, HttpResponseNotFound
from django.urls import reverse
from .models import Department, Course
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from .forms import DeptLogin, addCourseForm, addTeacherForm
from django.contrib import messages
from django.db import IntegrityError
import json, math
# Create your views here.

def homePage(request, deptId):
    # path('<str:deptId>/', views.homePage, name='home')
    try:
        dept = Department.objects.get(dept_id=deptId)
        return render(request, 'departments/home.html', {
            'dept': dept,
            'isLogged': request.user == dept.user
        })
    except Department.DoesNotExist:
        return HttpResponseRedirect(reverse('Main:home'))


def loginPage(request, deptId):
    # path('<str:deptId>/login/', views.loginPage, name='login')
    print(request.user.is_authenticated)
    if request.user.is_authenticated:
        return HttpResponseRedirect(reverse('dept:home', kwargs={'deptId': deptId}))

    form = DeptLogin(request.POST or None)

    if request.method == 'POST':
        if form.is_valid():
            dept = Department.objects.get(dept_id=deptId)
            user = authenticate(request, username=form.cleaned_data['department_name'], password=form.cleaned_data['password'])
            if user is not None:
                if user != dept.user:
                    messages.error(request, 'You are not authorized to login to another department')
                    return HttpResponseRedirect(reverse('dept:home', kwargs={'deptId': deptId}))
                login(request, user)
                return HttpResponseRedirect(reverse('dept:home', kwargs={'deptId': deptId}))
            else:

                form.add_error(None, 'Invalid username or password')
                return render(request, 'departments/login.html', {
                    'form': form
                })
        else:
            form.add_error(None, 'Invalid form')
            return render(request, 'departments/login.html', {
                'form': form
            })

    return render(request, 'departments/login.html', {
        'form': form
    })

def logoutPage(request, deptId):
    # path('<str:deptId>/logout/', views.logoutPage, name='logout')
    request.session.flush()
    logout(request)
    return HttpResponseRedirect(reverse('dept:home', kwargs={'deptId': deptId}))


def adminPage(request, deptId):
    # path('admin/<str:deptId>/', views.adminPage, name='admin')
    try:
        dept = Department.objects.get(dept_id=deptId)
        if request.user == dept.user:
            return render(request, 'departments/admin.html', {
                'dept': dept,
                "isLogged": True
            })
        else:
            messages.error(request, 'You are not authorized to access this page')
            return HttpResponseRedirect(reverse('Main:home'))
    except Department.DoesNotExist:
        return HttpResponseRedirect(reverse('Main:home'))
    
def modifyCourse(request, deptId):
    print(request.method)
    # path('admin/<str:deptId>/modify-course', views.modifyCourse, name='modifyCourse')
    # print the url
    print(request.get_full_path())
    # print the query string
    print(request.headers.get('X-Custom-Header','No X-Custom-Header'))
    try:
        dept = Department.objects.get(dept_id=deptId)
        if 'semester' not in request.session:
            request.session['semester'] = 1
        print(request.session['semester'])

        if request.user == dept.user:
            if request.method=='POST' and request.headers.get('X-Custom-Header','No X-Custom-Header') == 'deleteCourse':
                data = json.loads(request.body)
                course = Course.objects.get(title=data['courseID'])
                course.delete()
                messages.success(request, 'Course deleted successfully')
                print(course)
                return JsonResponse({'success': True}, safe=False)
            if request.headers.get('X-Custom-Header',None) == 'getCourseDescription':
                course = Course.objects.get(title=request.GET.get('course','No such query string'))
                des = json.loads(course.description)
                for k in des:
                    des[k] = des[k].replace('\r\n',', ').replace('.','').rstrip(',')+'.'
                des['title'] = course.title
                return JsonResponse(des, safe=False)

            return render(request, 'departments/modifyCourse.html', {
                'dept': dept,
                "isLogged": True,
                'recentSemester': request.session['semester']
            })
        else:
            messages.error(request, 'You are not authorized to access this page')
            return HttpResponseRedirect(reverse('Main:home'))
    except Department.DoesNotExist:
        return HttpResponseRedirect(reverse('Main:home'))
    except Course.DoesNotExist:
        messages.error(request, 'No such course')
        return HttpResponseRedirect(reverse('dept:modifyCourse', kwargs={'deptId': deptId}))

def addCourse(request, deptId):
    # path('admin/<str:deptId>/add-course', views.addCourse, name='addCourse')
    form = addCourseForm(request.POST or None)
    try:
        dept = Department.objects.get(dept_id=deptId)
        if request.user == dept.user:
            if request.method == 'POST':
                print(request.POST.get('totalTitles',None))
                totalTitles = int(request.POST.get('totalTitles','0'))
                descript = {}
                for i in range(totalTitles):
                    descript[request.POST.get('title'+str(i),'None')] = request.POST.get('Topic'+str(i),'None')
                print(descript)
                if form.is_valid():
                    title = form.cleaned_data['title']
                    name = form.cleaned_data['name']
                    Type = form.cleaned_data['type']
                    semester = form.cleaned_data['semester']
                    credit = form.cleaned_data['credit']
                    course = dept.courses.create(title=title, name=name, type=Type, semester=semester, credit=credit)
                    
                    # save to database in description field
                    course.description = json.dumps(descript)
                    course.save()

                    messages.success(request, 'Course added successfully')
                    return HttpResponseRedirect(reverse('dept:admin', kwargs={'deptId': deptId}))
                else:
                    form.add_error(None, 'Invalid form')
                    return render(request, 'departments/courseForm.html', {
                        'form': form,
                        'dept': dept,
                        "isLogged": True,
                        'descript': descript
                    })
            return render(request, 'departments/courseForm.html', {
                'form': form,
                'dept': dept,
                "isLogged": True,
                'descript': dict(),
            })
        else:
            messages.error(request, 'You are not authorized to access this page')
            return HttpResponseRedirect(reverse('Main:home'))
    except Department.DoesNotExist:
        return HttpResponseRedirect(reverse('Main:home'))
    

def courseTable(request, deptId, semester):
    # path('admin/<str:deptId>/course-table', views.courseTable, name='courseTable')
    try:
        print(request)
        dept = Department.objects.get(dept_id=deptId)
        if semester<1 or semester>8:
            raise ValueError('Invalid semester')
        request.session['semester'] = semester
        if request.user == dept.user:
            return render(request, 'departments/courseTable.html', {
                'dept': dept,
                'courses': dept.courses.filter(semester=semester),
                'year': math.ceil(semester/2),
                'semester': 'Odd' if semester%2==1 else 'Even',
            })
        else:
            messages.error(request, 'You are not authorized to access this page')
            return HttpResponseRedirect(reverse('Main:home'))
    except Department.DoesNotExist:
        return HttpResponseRedirect(reverse('Main:home'))
    except ValueError:
        messages.error(request, 'Invalid semester')
        return HttpResponseRedirect(dept.get_absolute_url())
    
def editCourse(request, deptId, courseId):
    # path('admin/<str:deptId>/edit-course/<str:courseId>', views.editCourse, name='editCourse')
    try:
        dept = Department.objects.get(dept_id=deptId)
        course = dept.courses.get(title=courseId)
        form = addCourseForm(request.POST or None, instance=course)
        if request.user == dept.user:
            if request.method == 'POST':
                if form.is_valid():
                    title = form.cleaned_data['title']
                    name = form.cleaned_data['name']
                    Type = form.cleaned_data['type']
                    semester = form.cleaned_data['semester']
                    credit = form.cleaned_data['credit']
                    course.title = title
                    course.name = name
                    course.type = Type
                    course.semester = semester
                    course.credit = credit
                    totalTitles = int(request.POST.get('totalTitles','0'))
                    descript = {}
                    for i in range(totalTitles):
                        descript[request.POST.get('title'+str(i),'None')] = request.POST.get('Topic'+str(i),'None')
                    print(descript)
                    course.description = json.dumps(descript)
                    course.save()
                    messages.success(request, 'Course edited successfully')
                    return HttpResponseRedirect(reverse('dept:modifyCourse', kwargs={'deptId': deptId}))
                else:
                    form.add_error(None, 'Invalid form')
                    return render(request, 'departments/courseForm.html', {
                        'form': form,
                        'dept': dept,
                        "isLogged": True,
                        'descript': json.loads(course.description)
                    })
            else:
                return render(request, 'departments/courseForm.html', {
                    'form': form,
                    'dept': dept,
                    "isLogged": True,
                    'descript': json.loads(course.description)
                })
        else:
            messages.error(request, 'You are not authorized to access this page')
            return HttpResponseRedirect(reverse('Main:home'))
    except Department.DoesNotExist:
        return HttpResponseRedirect(reverse('Main:home'))
    except Course.DoesNotExist:
        messages.error(request, 'Course does not exist')
        return HttpResponseRedirect(dept.get_absolute_url())

def deleteCourse(request, deptId, courseId):
    # TODO document why this method is empty
    pass


def addTeacher(request, deptId):
    # path('admin/<str:deptId>/add-teacher', views.addTeacher, name='addTeacher')
    form = addTeacherForm(request.POST or None, initial={'intro': 'No introductions yet.'})
    try:
        dept = Department.objects.get(dept_id=deptId)
        if request.user == dept.user:
            if request.method == 'POST':
                if form.is_valid():
                    code = form.cleaned_data['code']
                    name = form.cleaned_data['name']
                    designation = form.cleaned_data['designation']
                    intro = form.cleaned_data['intro']
                    dept.teachers.create(code=code, name=name, designation=designation, intro=intro)
                    messages.success(request, 'Teacher added successfully')
                    return HttpResponseRedirect(reverse('dept:admin', kwargs={'deptId': deptId}))
                else:
                    form.add_error(None, 'Invalid form')
                    return render(request, 'deptTeacher/addTeacher.html', {
                        'form': form,
                        'dept': dept,
                        "isLogged": True,
                    })
            return render(request, 'deptTeacher/addTeacher.html', {
                'form': form,
                'dept': dept,
                "isLogged": True,
            })
        else:
            messages.error(request, 'You are not authorized to access this page')
            return HttpResponseRedirect(reverse('Main:home'))

    except Department.DoesNotExist:
        return HttpResponseRedirect(reverse('Main:home'))
    except IntegrityError:
        form.add_error('code', 'Teacher with this code already exists')
        return render(request, 'deptTeacher/addTeacher.html', {
            'form': form,
            'dept': dept,
            "isLogged": True,
        })
    
def allTeachers(request, deptId):
    # path('admin/<str:deptId>/all-teachers', views.allTeachers, name='allTeachers')
    try:
        dept = Department.objects.get(dept_id=deptId)
        teachers = dept.teachers.all()
        return render(request, 'deptTeacher/allTeachers.html', {
            'dept': dept,
            'prof': teachers.filter(designation='Professor'),
            'assocProf': teachers.filter(designation='Associate Professor'),
            'asstProf': teachers.filter(designation='Assistant Professor'),
            'lect': teachers.filter(designation='Lecturer'),
            'isLogged': request.user == dept.user,
        })
    except Department.DoesNotExist:
        return HttpResponseNotFound('<h1>Page not found</h1>')