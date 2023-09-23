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
    dept = models.ForeignKey(Department, 
                             on_delete=models.CASCADE, 
                             related_name='students')
    section = models.ForeignKey(Section, 
                                on_delete=models.CASCADE, 
                                related_name='students')
    series = models.ForeignKey(Series, 
                               on_delete=models.CASCADE, 
                               related_name='students')
    cgpa = models.FloatField(null=True, blank=True)
    #courses = models.ManyToManyField(Course, related_name='students')
    # TODO remove this course field
    user = models.OneToOneField(User, 
                                on_delete=models.SET_NULL, 
                                null=True, blank=True, 
                                related_name='student')

    def __str__(self) -> str:
        return f'{self.roll}-{self.dept.dept_id}: {self.full_name}'


class StudentCourse(models.Model):
    student = models.ForeignKey(Student, 
                                on_delete=models.CASCADE, 
                                related_name='takes')
    course = models.ForeignKey(Course, 
                               on_delete=models.CASCADE, 
                               related_name='taken_by')
    completed = models.BooleanField(default=False)

class Exam(models.Model):
    id = models.AutoField(primary_key=True)
    examfor = models.ForeignKey(StudentCourse, 
                                on_delete=models.CASCADE, 
                                related_name='%(app_label)s_%(class)s_exams')
    total_marks = models.IntegerField()
    obtained_marks = models.IntegerField()
    grade = models.ForeignKey(GradePoint,
                              on_delete=models.CASCADE,
                              related_name='+') # '+' indicates: no reverse relation
    class Meta:
        abstract = True


class TheoryCourse(Exam):
    sectionA = models.IntegerField()
    sectionB = models.IntegerField()
    attendance = models.IntegerField()

    def calculate_total_marks(self):
        cts = self.examfor.class_tests.order_by('-full_marks').values_list('obtained_marks', flat=True)
        ct_total = round(sum(cts)/3)
        self.total_marks = self.sectionA + self.sectionB + self.attendance + ct_total


class LabCourse(Exam):
    viva = models.IntegerField()
    labPerformance = models.IntegerField()
    labReport = models.IntegerField(null=True, blank=True)
    attendance = models.IntegerField()
    labquiz = models.IntegerField(null=True, blank=True)
    labfinal = models.IntegerField(null=True, blank=True)
    def calculate_total_marks(self):
        self.total_marks = self.viva + self.labPerformance + self.labReport + self.attendance + self.labquiz + self.labfinal

class ClassTest(models.Model):
    id = models.AutoField(primary_key=True)
    full_marks = models.IntegerField()
    obtained_marks = models.IntegerField(default=0)
    taken_by = models.ForeignKey(Teacher, 
                                 on_delete=models.CASCADE, 
                                 related_name='class_tests')
    ct_for = models.ForeignKey(StudentCourse,
                               on_delete=models.CASCADE,
                               related_name='class_tests')    