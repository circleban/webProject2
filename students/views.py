from django.shortcuts import render
from .models import *
from departments.models import *
from Main.models import Transaction
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.http import HttpResponseRedirect, JsonResponse, HttpResponse
from django.urls import reverse
from .forms import *
import json
from django.http import HttpResponse


class TransactionError(Exception):
    pass


# Create your views here.


def home(request):
    if not request.user.is_authenticated:
        messages.error(request, "Login as a student first")
        return HttpResponseRedirect(reverse("students:login"))
    try:
        student = Student.objects.get(user=request.user)
        print(student)
    except Student.DoesNotExist:
        messages.error(request, "Login as a student first")
        return HttpResponseRedirect(reverse("students:login"))

    return render(
        request,
        "students/home.html",
        {
            "student": student,
            "courseRegRequired": student.series.courseReg.isRunning()
            and not student.takes.filter(
                course__semester=student.series.running_semester
            ).exists(),
        },
    )


def loginStudent(request):
    form = studentLoginForm(request.POST or None)
    if request.method == "POST":
        if form.is_valid():
            roll_no = form.cleaned_data.get("roll_no")
            password = form.cleaned_data.get("password")
            user = authenticate(request, username=roll_no, password=password)
            if user is not None:
                if not Student.objects.filter(user=user).exists():
                    messages.error(request, "You are not a student")
                    return HttpResponseRedirect(reverse("students:login"))
                login(request, user)
                return HttpResponseRedirect(reverse("students:home"))

        form.add_error(None, "Invalid Credentials")
        return render(request, "students/login.html", {"form": form})
    return render(request, "students/login.html", {"form": form})


def logoutStudent(request):
    request.session.flush()
    logout(request)
    return HttpResponseRedirect(reverse("Main:home"))


def courseReg(request):
    try:
        student = Student.objects.get(user=request.user)
        series = student.series
        if request.method == "POST":
            if request.headers.get("X-objective", None) == "proceed":
                print("in proceed")
                return JsonResponse(
                    {
                        "success": True,
                        "url": reverse("Main:payment"),
                    }
                )
            elif request.headers.get("X-objective", None) == "cancel":
                print("in cancel")
                return JsonResponse({"success": True, "url": reverse("students:home")})
            elif request.POST.get("submit", None) is not None:
                c_list = request.POST.getlist("courses")
                total_fee = 0.0
                fee = json.loads(series.courseReg.fee)
                course_list = []
                for i in c_list:
                    c = Course.objects.get(title=i)
                    course_list.append(c)
                    total_fee += float(c.credit) * (
                        fee["theory"] if c.isTheoryCourse() else fee["lab"]
                    )
                if total_fee == 0:
                    messages.error(request, "No course selected")
                    return HttpResponseRedirect(reverse("students:courseReg"))
                txn_id = request.POST.get("txn_id", None)
                try:
                    txn = Transaction.objects.get(
                        txn_id=txn_id, paid_by=student.user, paid_to=student.dept.user
                    )
                    if txn.is_expired():
                        messages.error(request, "Transaction Expired")
                        return HttpResponseRedirect(reverse("students:courseReg"))
                    print(txn, txn.txn_id)
                    print(total_fee)
                    print(type(txn.amount))
                    print(type(total_fee))
                    print(142.00 < total_fee)
                    if float(txn.amount) < total_fee:
                        messages.error(request, "Invalid Amount")
                        messages.error(request, "Amount paid: " + str(txn.amount))
                        messages.error(request, "Amount required: " + str(total_fee))
                        return HttpResponseRedirect(reverse("students:courseReg"))
                    for c in course_list:
                        try:
                            std_course = StudentCourse.objects.get(
                                student=student, course=c
                            )
                            std_course.registraion = "R"
                            std_course.save()
                        except StudentCourse.DoesNotExist:
                            std_course = StudentCourse.objects.create(
                                student=student, course=c
                            )
                        if c.isTheoryCourse():
                            TheoryCourse.objects.create(
                                examfor=std_course,
                            )
                            for _ in range(4):
                                ClassTest.objects.create(
                                    ct_for=std_course,
                                )
                            print(f"{c} - theory")
                        else:
                            LabCourse.objects.create(
                                examfor=std_course,
                            )
                            print(f"{c} - lab")

                    txn.set_expired()
                    messages.success(request, "Course Registration Successful")
                    return HttpResponseRedirect(reverse("students:home"))
                except Transaction.DoesNotExist:
                    messages.error(request, "Invalid Transaction ID")
                    return HttpResponseRedirect(reverse("students:courseReg"))
            HttpResponseRedirect(reverse("students:courseReg"))
        courses = Course.objects.filter(semester=series.running_semester)

        fees = json.loads(series.courseReg.fee)

        cd = {
            c.title: {
                "name": c.name,
                "credits": c.credit,
                "type": c.type,
                "fee": float(c.credit)
                * (fees["theory"] if c.isTheoryCourse() else fees["lab"]),
            }
            for c in courses
        }

        return render(
            request,
            "students/courseReg.html",
            {
                "student": student,
                "courses": cd,
            },
        )
    except Student.DoesNotExist:
        messages.error(request, "Login as a student first")
        return HttpResponseRedirect(reverse("students:login"))


def results(request):
    if not request.user.is_authenticated:
        messages.error(request, "Login as a student first")
        return HttpResponseRedirect(reverse("students:login"))
    try:
        student = Student.objects.get(user=request.user)
        all_students = Student.objects.filter(series=student.series)
        results = {
            std: {
                'result': std.results.latest("semester"),
                'total_credit': sum([r.obtained_credit for r in std.results.all()]),
            }
            for std in all_students
        }
        return render(
            request,
            "students/results.html",
            {"student": student, 
             'semester': student.dept.semesters.get(sem_no = student.series.running_semester.sem_no-1),
             "results": results},
        )

    except Student.DoesNotExist:
        messages.error(request, "Login as a student first")
        return HttpResponseRedirect(reverse("students:login"))
