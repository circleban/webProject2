from collections.abc import Iterable
from django.db import models
from departments.models import *
from Main.models import Person
from django.contrib.auth.models import User
from teachers.models import Teacher

# Create your models here.


class Student(Person):
    roll = models.CharField(unique=True, max_length=7)
    # name = models.CharField(max_length=50)
    # phone_no = models.CharField(max_length=15, null=True, blank=True)
    dept = models.ForeignKey(
        Department, on_delete=models.CASCADE, related_name="students"
    )
    section = models.ForeignKey(
        Section, on_delete=models.CASCADE, related_name="students"
    )
    series = models.ForeignKey(
        Series, on_delete=models.CASCADE, related_name="students"
    )
    cgpa = models.DecimalField(max_digits=3, decimal_places=2 ,null=True, blank=True)

    user = models.OneToOneField(
        User, on_delete=models.SET_NULL, null=True, blank=True, related_name="student"
    )

    class Meta:
        ordering = ['roll']

    def __str__(self) -> str:
        return f"{self.roll}-{self.dept.dept_id}: {self.full_name}"


class StudentCourse(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name="takes")
    course = models.ForeignKey(
        Course, on_delete=models.CASCADE, related_name="taken_by"
    )
    registraion = models.CharField(
        max_length=10,
        choices=[("R", "Registered"), ("N", "Not Registered")],
        default="R",
    )
    completed = models.BooleanField(default=False)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["student", "course"], name="unique_student_course"
            )
        ]

    def __str__(self) -> str:
        if self.completed:
            comp = 'Completed'
        else:
            comp = 'Not Completed'
        return f"{self.student.roll}-{self.course.title}: {self.registraion} --- {comp}"


class Exam(models.Model):
    id = models.AutoField(primary_key=True)
    examfor = models.ForeignKey(
        StudentCourse,
        on_delete=models.CASCADE,
        related_name="%(app_label)s_%(class)s_exams",
    )
    total_marks = models.IntegerField(default=100)
    obtained_marks = models.IntegerField(null=True, blank=True)
    grade = models.ForeignKey(
        GradePoint, on_delete=models.CASCADE, related_name="+", null=True, blank=True
    )  # '+' indicates: no reverse relation

    class Meta:
        abstract = True

    def set_grade(self):
        if self.obtained_marks:
            self.grade = GradePoint.objects.filter(
                minimum_marks__lte=self.obtained_marks,
                maximum_marks__gte=self.obtained_marks,
            ).first()


class TheoryCourse(Exam):
    sectionA = models.IntegerField(null=True, blank=True)
    sectionB = models.IntegerField(null=True, blank=True)
    attendance = models.IntegerField(null=True, blank=True)

    def calculate_total_marks(self):
        self.obtained_marks = self.get_total_marks()
        self.set_grade()
        if self.grade.grade != 'F':
            self.examfor.completed = True
            self.examfor.registration = 'N'
            self.examfor.save()
        self.save()

    def get_ct_total(self):
        cts = self.examfor.class_tests.order_by("-obtained_marks").values_list(
            "obtained_marks", flat=True
        )
        return round(sum([(i or 0) for i in cts[:3]]) / 3)

    def get_semester_final_marks(self):
        return self.sectionA + self.sectionB + self.attendance

    def get_total_marks(self):
        return self.get_semester_final_marks() + self.get_ct_total()

    def __str__(self) -> str:
        return f"{self.examfor.student.roll}-{self.examfor.course.title}: {self.obtained_marks}"


class LabCourse(Exam):
    viva = models.IntegerField(null=True, blank=True)
    labPerformance = models.IntegerField(null=True, blank=True)
    labReport = models.IntegerField(null=True, blank=True)
    attendance = models.IntegerField(null=True, blank=True)
    labquiz = models.IntegerField(null=True, blank=True)
    labfinal = models.IntegerField(null=True, blank=True)

    def calculate_total_marks(self):
        self.obtained_marks = self.get_total_marks()
        self.set_grade()
        if self.grade.grade != 'F':
            self.examfor.completed = True
            self.examfor.registration = 'N'
            self.examfor.save()
        self.save()

    def get_total_marks(self):
        return (
            (self.viva or 0)
            + (self.labPerformance or 0)
            + (self.labReport or 0)
            + (self.attendance or 0)
            + (self.labquiz or 0)
            + (self.labfinal or 0)
        )

    def __str__(self) -> str:
        return f"{self.examfor.student.roll}-{self.examfor.course.title}: {self.obtained_marks}"


class ClassTest(models.Model):
    id = models.AutoField(primary_key=True)
    full_marks = models.IntegerField(default=20)
    obtained_marks = models.IntegerField(null=True, blank=True)
    taken_by = models.ForeignKey(
        Teacher,
        on_delete=models.CASCADE,
        related_name="class_tests",
        null=True,
        blank=True,
    )
    ct_for = models.ForeignKey(
        StudentCourse, on_delete=models.CASCADE, related_name="class_tests"
    )

    def __str__(self) -> str:
        return f"{self.id}:: {self.ct_for.student.roll}-{self.ct_for.course.title}: {self.obtained_marks}"


class Result(models.Model):
    id = models.AutoField(primary_key=True)
    student = models.ForeignKey(
        Student, on_delete=models.CASCADE, related_name="results"
    )
    semester = models.ForeignKey(
        Semester, on_delete=models.CASCADE, related_name="results"
    )
    total_credit = models.IntegerField(null=True, blank=True)
    obtained_credit = models.IntegerField(null=True, blank=True)
    gpa = models.DecimalField(max_digits=3, decimal_places=2, null=True, blank=True)

    def calculate_result(self):
        import numpy as np
        total_credit = 0
        obtained_credit = 0
        for c in self.student.takes.filter(course__semester=self.semester):
            for t in c.course.teachers.all():
                t.finish_course()
            if c.course.isTheoryCourse():
                c.students_theorycourse_exams.latest("id").calculate_total_marks()
            else:
                c.students_labcourse_exams.latest("id").calculate_total_marks()

        for c in self.student.takes.filter(course__semester=self.semester):    
            total_credit += c.course.credit
            if c.completed:
                obtained_credit += c.course.credit
        cigi, ci = self.calculate_cumulative_points(
            self.student.takes.filter(course__semester=self.semester)
        )
        self.gpa = cigi / ci
        cigi, ci = tuple(
            np.add(
                (cigi, ci),
                self.calculate_cumulative_points(
                    self.student.takes.exclude(course__semester=self.semester)
                ),
            )
        )
        self.student.cgpa = cigi / ci
        self.student.save()
        self.total_credit = total_credit
        self.obtained_credit = obtained_credit

    def calculate_cumulative_points(self, studentCourse):
        cigi, ci = 0.0, 0.0
        for c in studentCourse:
            if c.course.isTheoryCourse():
                exam = c.students_theorycourse_exams.latest("id")
            else:
                exam = c.students_labcourse_exams.latest("id")
            exam.calculate_total_marks()
            cigi += float(exam.grade.point) * float(c.course.credit)
            ci += float(c.course.credit)
        return cigi, ci

    def save(self, *args, **kwargs):
        self.calculate_result()
        super(Result, self).save(*args, **kwargs)
