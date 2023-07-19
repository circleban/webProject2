from django.db import models
from departments.models import *
from Main.models import Person
from django.contrib.auth.models import User
# Create your models here.

class Student(Person):
    roll = models.CharField(unique=True, max_length=7)
    # name = models.CharField(max_length=50)
    # phone_no = models.CharField(max_length=15, null=True, blank=True)
    dept = models.ForeignKey(Department, on_delete=models.CASCADE, related_name='students')
    section = models.ForeignKey(Section, on_delete=models.CASCADE, related_name='students')
    series = models.ForeignKey(Series, on_delete=models.CASCADE, related_name='students')
    semester = models.ForeignKey(Semester, on_delete=models.CASCADE, related_name='students', null=True, blank=True)
    courses = models.ManyToManyField(Course, related_name='students')
    user = models.OneToOneField(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='student')

    def __str__(self) -> str:
        return f'{self.roll}-{self.dept.dept_id}: {self.full_name}'