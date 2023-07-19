from django.contrib import admin
from .models import Teacher
# Register your models here.

class TeacherAdmin(admin.ModelAdmin):
    list_display = ('code','full_name', 'designation', 'dept')
    list_filter = ('designation', 'dept')
    search_fields = ('full_name', 'designation', 'dept')
    list_per_page = 25

admin.site.register(Teacher, TeacherAdmin)
