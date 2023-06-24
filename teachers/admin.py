from django.contrib import admin
from .models import Teacher
# Register your models here.

class TeacherAdmin(admin.ModelAdmin):
    list_display = ('name', 'designation', 'dept')
    list_filter = ('designation', 'dept')
    search_fields = ('name', 'designation', 'dept')
    list_per_page = 25

admin.site.register(Teacher, TeacherAdmin)
