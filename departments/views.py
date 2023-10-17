from django.shortcuts import render
from django.http import HttpResponseRedirect, JsonResponse, HttpResponseNotFound
from django.urls import reverse
from .models import Department, Course, Semester
from students.models import *
from Main.models import Notification
from teachers.models import courseTeacherAssignment
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from .forms import *
from django.contrib import messages
from django.db import IntegrityError
import json, math, datetime
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
                    dept.semesters.create(sem_no=i)
                return JsonResponse({'success':True})
        return render(request, 'departments/allSemester.html', {
            'dept': dept,
            'semesters': semesters,
            'isLogged': request.user == dept.user,
        })
    except Department.DoesNotExist:
        return HttpResponseNotFound('<h1>Page not found</h1>')
    
def addSeries(request, deptId):
    try:
        dept = Department.objects.get(dept_id=deptId)
        if request.user == dept.user:
            if request.method == 'POST':
                print(request.headers.get('X-Custom-Headers','Nope'))
                if request.headers.get('X-Custom-Headers',None) == 'addSeries':
                    form = addSeriesForm(request.POST) 
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
                        return JsonResponse({'status':'seriesDone', 'html':html.content.decode('utf-8')})
                        
                    else:
                        form.add_error(None, 'Invalid form')
                        err = render(request, 'series/addSeries.html', {
                            'dept': dept,
                            'form': form,
                            'isLogged': True,
                        })
                        return JsonResponse({'status':'seriesFailed', 'html':err.content.decode('utf-8')})
                elif request.headers.get('X-Custom-Headers',None) == 'addStudent':
                    try:
                        serID = request.POST.get('series',None)
                        series = Series.objects.get(id=int(serID))
                        roll_l = lambda x: str(x) if x>99 else '0'+str(x) if x>9 else '00'+str(x)
                        serID = series.name[-2:]
                        rolls = {i: serID+dept.dept_code+roll_l(i+1) for i in range(0, series.maximum_students)}
                        for i in range(0, series.maximum_students):
                            name = request.POST.get('name-'+rolls[i],None)
                            email = request.POST.get('email-'+rolls[i],None)
                            sec = request.POST.get('section-'+rolls[i],None)
                            section = Section.objects.get(name=series.name+sec)
                            suser = User.objects.create_user(username=rolls[i], password='AwKatenI')
                            series.students.create(roll=rolls[i], full_name=name, email=email, section=section, dept=dept, user=suser)
                        messages.success(request, 'Students added successfully')
                        return JsonResponse({'status':'studentDone'})

                    except:
                        messages.error(request, 'Series not found')
                        return JsonResponse({'status':'studentFailed'})
            else:
                return render(request, 'series/addSeries.html', {
                'dept': dept,
                'form': addSeriesForm(),
                'isLogged': True,
                })
        else:
            messages.error(request, 'You are not authorized to access this page')
            return HttpResponseRedirect(reverse('Main:home'))

    except Department.DoesNotExist:
        return HttpResponseNotFound('<h1>Page not found</h1>')
    
def allSeries(request, deptId):
    try:
        dept = Department.objects.get(dept_id=deptId)
        if request.user == dept.user:
            return render(request, 'series/allSeries.html', {
                'dept': dept,
                'ongoing_series': dept.series.filter(is_running=True),
                'grad_series': dept.series.filter(is_running=False),
                'isLogged': True,
            })
        else:
            messages.error(request, 'You are not authorized to access this page')
            return HttpResponseRedirect(reverse('Main:home'))
        
    except Department.DoesNotExist:
        return HttpResponseNotFound('<h1>Page not found</h1>')

def allStudents(request, deptId):
    try:
        dept = Department.objects.get(dept_id=deptId)
        serID = request.GET.get('series',None)
        series = None if serID is None else dept.series.get(id=int(serID))
        students = dept.students.all() if series is None else series.students.all()
        if request.user == dept.user:
            return render(request, 'series/allStudents.html', {
                'dept': dept,
                'series': series,
                'students': students,
                'isLogged': True,
            })
        else:
            messages.error(request, 'You are not authorized to access this page')
            return HttpResponseRedirect(reverse('Main:home'))
        
    except Department.DoesNotExist:
        return HttpResponseNotFound('<h1>Page not found</h1>')
    
def seriesControlPanel(request, deptId, serId):
    try:
        dept = Department.objects.get(dept_id=deptId)
        series = dept.series.get(id=serId)
        if request.user == dept.user:
            if request.method == 'POST':
                print('Got a post request in seriesControlPanel')
                return seriesControl_post_request(request, dept, series)
                

            series.courseReg.check_deadline()
            return render(request, 'series/seriesControlPanel.html', {
                'dept': dept,
                'series': series,
                'today': datetime.date.today().strftime('%Y-%m-%d'),
                'isLogged': True,
            })
        else:
            messages.error(request, 'You are not authorized to access this page')
            return HttpResponseRedirect(reverse('Main:home'))
        
    except Department.DoesNotExist:
        return HttpResponseNotFound('<h1>Page not found</h1>')
    except Series.DoesNotExist:
        return HttpResponseNotFound('<h1>Page not found</h1>')
def seriesControl_post_request(request, dept, series):
    if request.POST.get('controls', None) == 'courseReg':
        print('In courseReg')
        today = request.POST.get('today',None)
        deadline = request.POST.get('deadline',None)
        fee = {
            'theory': float(request.POST.get('theoryFee',None)),
            'lab': float(request.POST.get('labFee',None)),
        }
        print(deadline, fee)
        courseReg = series.courseReg
        courseReg.status = 'running'
        courseReg.start_date = today
        courseReg.end_date = deadline
        courseReg.fee = json.dumps(fee)
        courseReg.save()
        return HttpResponseRedirect(series.get_absolute_url_control_panel())
    elif request.POST.get('controls', None) == 'announce-exam':
        print('Announce exam')
        series.exam_status = 'R'
        series.save()
        start_date = request.POST.get('start-date',None)
        for student in series.students.all():
            Notification.objects.create(
                From = dept.user,
                to=student.user, 
                title='Exam announced', 
                message= f'''Exam has been announced for your series. Exam will start from {start_date}''',
                )
        return HttpResponseRedirect(series.get_absolute_url_control_panel())
    elif json.load(request).get('controls', None) == 'end-exam':
        print('End exam')
        series.exam_status = 'F'
        series.save()
        return JsonResponse({'success':True})


def courseTeacherAllocation(request, deptId, serId):
    print(request.get_full_path())
    try:
        dept = Department.objects.get(dept_id=deptId)
        series = dept.series.get(id=serId)
        if request.user == dept.user:
            if request.method == 'POST':
                try:
                    print('Got a post request in courseTeacherAllocation')
                    data = json.loads(request.body)
                    print(data) 
                    course = Course.objects.get(title=data['courseID'])
                    dpt = Department.objects.get(dept_id=data['dept'])
                    teachers = data['teachers']
                    print(len(series.allocations.all()))
                    for t in teachers:
                        teacher = dpt.teachers.get(code=t)
                        courseTeacherAssignment.objects.create(course=course, 
                                                               teacher=teacher, 
                                                               series=series)
                    html_content = '''
                        <div class="row mx-2">
                            <p class="text-primary-emphasis fw-bold font-monospace">List of Instructors for this course</p>
                            <ul class="list-group list-group-numbered list-group-flush" id="selected-teachers">
                    '''

                    for teacher in course.teachers.all():
                        html_content += f'''
                                <li class="list-group-item fw-semibold custom-font">{teacher.teacher.full_name}, {teacher.teacher.designation},
                                    Department of {teacher.teacher.dept.dept_name}
                                </li>
                        '''

                    html_content += '''
                            </ul>
                        </div>
    '''                
                    return JsonResponse({'success':True, 'html':html_content})
                except Exception as e:
                    print('Error:',e)
                    return JsonResponse({'success':False})
            elif request.method == 'GET':
                if request.GET.get('listFor', None) is not None:
                    print(request.GET.get('listFor'))
                    listFor = request.GET.get('listFor')
                    try:
                        dpt = Department.objects.get(dept_id=listFor)
                        teachers = dpt.teachers.all()
                        dt = {t.code: f'{t.full_name} - {t.designation}' for t in teachers}
                        return JsonResponse({
                            'success':True,
                            'teachers': dt
                        })
                    except Department.DoesNotExist:
                        return JsonResponse({'success':False})

                else:
                    return render(request, 'series/courseAllocation.html', {
                        'dept': dept,
                        'allDepts': Department.objects.all(),
                        'series': series,
                        'courses': dept.courses.filter(semester=series.running_semester),
                        'isLogged': True,
                    })
        else:
            messages.error(request, 'You are not authorized to access this page')
            return HttpResponseRedirect(reverse('Main:home'))
        
    except Department.DoesNotExist:
        return HttpResponseNotFound('<h1>Page not found</h1>')
    except Series.DoesNotExist:
        return HttpResponseNotFound('<h1>Page not found</h1>')
    
def result(request, deptId, serId):
    try:
        dept = Department.objects.get(dept_id=deptId)
        series = dept.series.get(id=serId)
        if request.user == dept.user:
            if request.method == 'POST':
                print('Got a post request in result')
                if request.POST.get('action') == 'publish':
                    print('Publishing result')
                    students = series.students.all()
                    for student in students:
                        student.results.create(semester = series.running_semester)
                        Notification.objects.create(
                            From = dept.user,
                            to=student.user, 
                            title='Result published', 
                            message= '''Result has been published for your series. You can check your result now.''',
                            )
                    series.complete_semester()
                    messages.success(request, 'Result published successfully')
                elif request.POST.get('action') == 'cancel':
                    messages.success(request, 'Result publishing cancelled')
                return HttpResponseRedirect(series.get_absolute_url_control_panel())
            else:
                context = {}
                courses = dept.courses.filter(semester=series.running_semester)
                for c in courses:
                    sc = c.taken_by.all()
                    m = {}
                    for s in sc:
                        try:
                            theory = s.students_theorycourse_exams.latest('id')
                        except TheoryCourse.DoesNotExist:
                            theory = None
                        try:
                            lab = s.students_labcourse_exams.latest('id')
                        except LabCourse.DoesNotExist:
                            lab = None
                        m[s.student.roll] = {
                            'student': s.student,
                            'theory': theory,
                            'lab': lab,
                        }
                    context[c.title] = {
                        'course': c,
                        'marks': m,
                    }
                        
                return render(request, 'series/result.html', {
                    'dept': dept,
                    'series': series,
                    'marks': context,
                    'isLogged': True,
                })
        else:
            messages.error(request, 'You are not authorized to access this page')
            return HttpResponseRedirect(reverse('Main:home'))
        
    except Department.DoesNotExist:
        return HttpResponseNotFound('<h1>Page not found</h1>')
    except Series.DoesNotExist:
        return HttpResponseNotFound('<h1>Page not found</h1>')