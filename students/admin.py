from django.contrib import admin
from .models import *
# Register your models here.

class StudentAdmin(admin.ModelAdmin):
    list_display = ('roll', 'name', 'phone_no', 'dept', 'section', 'series')
    list_filter = ('dept', 'section', 'series')
    search_fields = ('roll', 'name', 'phone_no', 'dept', 'section', 'series')
    list_per_page = 25

admin.site.register(Student, StudentAdmin)