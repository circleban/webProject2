from django.contrib import admin
from .models import *

# Register your models here.

class DepartmentAdmin(admin.ModelAdmin):
    list_display = ('dept_id', 'dept_code', 'dept_name', 'head')
    list_filter = ('dept_id', 'dept_code')
    search_fields = ('dept_id', 'dept_code', 'dept_name')
    list_per_page = 25

class CourseAdmin(admin.ModelAdmin):
    list_display = ('title', 'name', 'type', 'semester', 'isAllocated', 'credit', 'department')
    list_filter = ('type', 'semester', 'isAllocated', 'credit')
    search_fields = ('title', 'name', 'type', 'semester', 'isAllocated', 'credit', 'department')
    list_per_page = 25

class SeriesAdmin(admin.ModelAdmin):
    list_display = ('name', 'admit_year', 'running_semester', 'is_running', 'department')
    list_filter = ('admit_year', 'running_semester', 'is_running')
    search_fields = ('name', 'admit_year', 'running_semester', 'is_running', 'department')
    list_per_page = 25

admin.site.register(Department, DepartmentAdmin)
admin.site.register(Course,CourseAdmin)
admin.site.register(Series, SeriesAdmin)
admin.site.register(Section)


