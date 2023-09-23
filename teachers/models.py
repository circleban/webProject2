from django.db import models
from django.contrib.auth.models import User
from departments.models import *
from Main.models import Person
# Create your models here.

class Teacher(Person):
    code = models.CharField(max_length=5)
    user = models.OneToOneField(User, 
                                on_delete=models.SET_NULL, 
                                null=True, blank=True, 
                                related_name='teacher')
    dept = models.ForeignKey(Department, 
                             on_delete=models.CASCADE, 
                             related_name='teachers')
    joined = models.DateField(auto_now_add=True)
    intro = models.TextField(null=True, blank=True)
    
    prof = 'Professor'
    asst_prof = 'Assistant Professor'
    assoc_prof = 'Associate Professor'
    lecturer = 'Lecturer'
    teacher_type_choices = [
        (prof, 'Professor'),
        (asst_prof, 'Assistant Professor'),
        (assoc_prof, 'Associate Professor'),
        (lecturer, 'Lecturer')
    ]
    designation = models.CharField(max_length=20, 
                                   choices=teacher_type_choices, 
                                   default=lecturer)
        
    active = "Active"
    leave = "On Leave"
    ret = "Retired"
    teacher_status_choices = [
        (active, "Active"),
        (leave, "On Leave"),
        (ret, "Retired")
    ]
    status = models.CharField(max_length=10, 
                              choices=teacher_status_choices, 
                              default=active)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['code', 'dept'], name='unique_teacher')
        ]

    def __str__(self) -> str:
        return f'{self.code}-{self.dept.dept_id}: {self.full_name} ({self.designation})'

class courseTeacherAssignment(models.Model):
    id = models.AutoField(primary_key=True)
    course = models.ForeignKey(Course, 
                               on_delete=models.CASCADE, 
                               related_name='teachers')
    teacher = models.ForeignKey(Teacher, 
                                on_delete=models.CASCADE, 
                                related_name='courses')
    series = models.ForeignKey(Series, 
                               on_delete=models.CASCADE, 
                               related_name='allocations')
    section = models.ForeignKey(Section, 
                                on_delete=models.CASCADE, 
                                related_name='allocations',
                                null=True, blank=True)
    status = models.CharField(max_length=10, 
                              choices=[('Active', 'Active'), 
                                       ('Finished', 'Finished')], 
                                       default='Active')
    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['course', 'teacher', 'series', 'section'], name='unique_course_teacher')
        ]