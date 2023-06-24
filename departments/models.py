from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse
# Create your models here.

class Department(models.Model):
    dept_id = models.CharField(max_length=4, unique=True)
    dept_code = models.CharField(max_length=5, unique=True, null=True, blank=True)
    dept_name = models.CharField(max_length=50)
    head = models.OneToOneField('teachers.Teacher', on_delete=models.SET_NULL, null=True, blank=True, related_name='dept_head') 
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True, related_name='dept')
    def __str__(self) -> str:
        return f'{self.dept_id}: {self.dept_name}'
    
    def get_absolute_url(self):
        return reverse('dept:home', kwargs={'deptId': self.dept_id})
    

class Course(models.Model):
    th = "Theory"
    lab = "Lab"
    type_choices = [
        (th, "Theory"),
        (lab, "Lab")
    ]

    title = models.CharField(max_length=10, unique=True)
    name = models.CharField(max_length=64)
    type = models.CharField(max_length=10, choices=type_choices, default=th)
    semester = models.IntegerField()
    isAllocated = models.BooleanField(default=False)
    credit = models.DecimalField(max_digits=3, decimal_places=2, default=0.00)
    department = models.ForeignKey(Department, on_delete=models.CASCADE, related_name='courses')
    description = models.JSONField(null=True, blank=True)

    class Meta:
        ordering = ['semester', 'title']

    def __str__(self) -> str:
        return f'{self.title}: {self.name}, Semester: {self.semester}'
    
    def isTheoryCourse(self):
        return self.type == self.th

    def edit_course_url(self):
        return reverse('dept:editCourse', kwargs={'deptId': self.department.dept_id, 'courseId': self.title})
    def delete_course_url(self):
        return reverse('dept:deleteCourse', kwargs={'deptId': self.department.dept_id, 'courseId': self.title})
    

class Series(models.Model):
    name = models.CharField(max_length=10, unique=True)
    department = models.ForeignKey(Department, on_delete=models.CASCADE, related_name='series')
    admit_year = models.IntegerField()
    running_semester = models.IntegerField()
    is_running = models.BooleanField(default=True)
    def __str__(self) -> str:
        return f'{self.name}, {self.admit_year}, Running semester: {self.running_semester}'
    

class Section(models.Model):
    name = models.CharField(max_length=10, unique=True) #Ex - CSE19A
    series = models.ForeignKey(Series, on_delete=models.CASCADE, related_name='sections')
    def __str__(self) -> str:
        return f'{self.name}, {self.series.name}'