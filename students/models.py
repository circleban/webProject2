from django.db import models
from departments.models import *
# Create your models here.

class Student(models.Model):
    roll = models.IntegerField(unique=True)
    name = models.CharField(max_length=50)
    phone_no = models.CharField(max_length=15, null=True, blank=True)
    dept = models.ForeignKey(Department, on_delete=models.CASCADE, related_name='students')
    section = models.ForeignKey(Section, on_delete=models.CASCADE, related_name='students')
    series = models.ForeignKey(Series, on_delete=models.CASCADE, related_name='students')
    courses = models.ManyToManyField(Course, related_name='students')

    def __str__(self) -> str:
        return f'{self.roll}-{self.dept.dept_id}: {self.name}'