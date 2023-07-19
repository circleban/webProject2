from django.shortcuts import render
from django.http import HttpResponseRedirect, JsonResponse, HttpResponseNotFound
from django.urls import reverse
from .models import Department, Course, Semester
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from .forms import *
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
            if request.method == 'POST' and request.headers.get('X-Custom-Header','No X-Custom-Header') == 'deleteCourse':
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
                    sem_id = form.cleaned_data['semester']
                    credit = form.cleaned_data['credit']
                    semester = Semester.objects.get(id=sem_id, dept=dept)
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
    

def courseTable(request, deptId, semester_id):
    # path('admin/<str:deptId>/course-table', views.courseTable, name='courseTable')
    try:
        print(request)
        dept = Department.objects.get(dept_id=deptId)
        if semester_id<1 or semester_id>8:
            raise ValueError('Invalid semester')
        request.session['semester'] = semester_id
        if request.user == dept.user:
            semester = Semester.objects.get(id=semester_id, dept=dept)
            return render(request, 'departments/courseTable.html', {
                'dept': dept,
                'courses': dept.courses.filter(semester=semester),
                'year': semester.year,
                'semester': semester.year_sem,
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
                    semester_id = form.cleaned_data['semester']
                    credit = form.cleaned_data['credit']
                    course.title = title
                    course.name = name
                    course.type = Type
                    semester = Semester.objects.get(id=semester_id, dept=dept)
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
                form.initial['semester'] = course.semester.id
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
                    # code = form.cleaned_data['code']
                    # full_name = form.cleaned_data['f_name'].split()
                    # first_name = ' '.join(full_name[:-1])
                    # last_name = full_name[-1]
                    # designation = form.cleaned_data['designation']
                    # intro = form.cleaned_data['intro']
                    # dept.teachers.create(code=code, first_name=first_name, last_name=last_name, designation=designation, intro=intro)
                    kw = {'dept': dept}
                    form.save(**kw)
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

def allSemesters(request, deptId):
    # path('admin/<str:deptId>/allSemesters', views.allSemesters, name='allSemesters')
    try:
        dept = Department.objects.get(dept_id=deptId)
        semesters = dept.semesters.all()
        if request.headers.get('X-Custom-Header',None) == 'createSemester':
            count = int(request.GET.get('count',None))
            if count<1 or count>8:
                messages.error(request, 'Invalid semester count')
                return JsonResponse({'success':False})
            else:
                for i in range(1,count+1):
                    dept.semesters.create(id=i)
                return JsonResponse({'success':True})
        return render(request, 'departments/allSemester.html', {
            'dept': dept,
            'semesters': semesters,
            'noOfStudents': {semester.id: semester.students.count() for semester in semesters},
            'isLogged': request.user == dept.user,
        })
    except Department.DoesNotExist:
        return HttpResponseNotFound('<h1>Page not found</h1>')
    
def addSeries(request, deptId):
    try:
        dept = Department.objects.get(dept_id=deptId)
        if request.user == dept.user:
            form = addSeriesForm(request.POST or None)
            if request.method == 'POST':
                print(request.headers.get('X-Custom-Headers','Nope'))
                if request.headers.get('X-Custom-Headers',None) == 'addSeries':
                    if form.is_valid():
                        kw = {'dept': dept}
                        series = form.save(**kw)
                        serID = series.name[-2:]
                        print(serID)
                        roll = lambda x: str(x) if x>99 else '0'+str(x) if x>9 else '00'+str(x)
                        rolls = {i: serID+dept.dept_code+roll(i+1) for i in range(0, series.maximum_students)}
                        messages.success(request, 'Series added successfully')
                        html = render(request, 'series/addStudents.html', {
                            'dept': dept,
                            'series': series,
                            'rolls': rolls,
                            'students_per_section': series.maximum_students//len(series.sections.all()),
                            'isLogged': True,
                        })
                        return JsonResponse({'success':True, 'html':html.content.decode('utf-8')})
                        
                    else:
                        form.add_error(None, 'Invalid form')
                        err = render(request, 'series/addSeries.html', {
                            'dept': dept,
                            'form': form,
                            'isLogged': True,
                        })
                        return JsonResponse({'success':False, 'html':err.content.decode('utf-8')})

            return render(request, 'series/addSeries.html', {
                'dept': dept,
                'form': form,
                'isLogged': True,
            })
        else:
            messages.error(request, 'You are not authorized to access this page')
            return HttpResponseRedirect(reverse('Main:home'))

    except Department.DoesNotExist:
        return HttpResponseNotFound('<h1>Page not found</h1>')