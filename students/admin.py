from django.contrib import admin
from .models import *
# Register your models here.

class StudentAdmin(admin.ModelAdmin):
    list_display = ('roll', 'full_name', 'phone', 'dept', 'section', 'series')
    list_filter = ('dept', 'section', 'series')
    search_fields = ('roll', 'full_name', 'phone', 'dept', 'section', 'series')
    list_per_page = 25

class StudentCourseAdmin(admin.ModelAdmin):
    list_display = ('get_student_roll','get_student_name', 'get_course_id','get_course_name','get_semester', 'completed')
    # list_filter = ('student', 'course', 'completed')
    # search_fields = ('student', 'course', 'completed')
    list_per_page = 25
    @admin.display(description='Roll No')
    def get_student_roll(self, obj):
        return obj.student.roll
    @admin.display(description='Student Name')
    def get_student_name(self, obj):
        return obj.student.full_name
    @admin.display(description='Course ID')
    def get_course_id(self, obj):
        return obj.course.title
    @admin.display(description='Course Name')
    def get_course_name(self, obj):
        return obj.course.name
    @admin.display(description='Semester')
    def get_semester(self, obj):
        return obj.course.semester
class LabCourseAdmin(admin.ModelAdmin):
    list_display = ('id', 'roll_no', 'course_title', 'labPerformance', 'attendance', 'labReport', 'viva', 'labquiz', 'labfinal', 'obtained_marks')
    list_filter = ('examfor__student__dept', 'examfor__student__section', 'examfor__course__title')
    @admin.display(description='Roll No')
    def roll_no(self, obj):
        return obj.examfor.student.roll
    @admin.display(description='Course Title')
    def course_title(self, obj):
        return obj.examfor.course.title
# same for theory course
class TheoryCourseAdmin(admin.ModelAdmin):
    list_display = ('id', 'roll_no', 'course_title', 'sectionA','sectionB', 'obtained_marks')
    list_filter = ('examfor__student__dept', 'examfor__student__section', 'examfor__course__title')
    @admin.display(description='Roll No')
    def roll_no(self, obj):
        return obj.examfor.student.roll
    @admin.display(description='Course Title')
    def course_title(self, obj):
        return obj.examfor.course.title    

class ResultAdmin(admin.ModelAdmin):
    list_display = ('id', 'roll_no', 'semester', 'total_credit', 'obtained_credit', 'gpa')
    list_filter = ('student__dept', 'student__section', 'semester')
    @admin.display(description='Roll No')
    def roll_no(self, obj):
        return obj.student.roll

admin.site.register(Student, StudentAdmin)
admin.site.register(StudentCourse, StudentCourseAdmin)
admin.site.register(TheoryCourse, TheoryCourseAdmin)
admin.site.register(LabCourse, LabCourseAdmin)
admin.site.register(ClassTest)
admin.site.register(Result, ResultAdmin) 