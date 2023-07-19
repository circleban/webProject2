from django.contrib import admin
from .models import *
# Register your models here.

class StudentAdmin(admin.ModelAdmin):
    list_display = ('roll', 'full_name', 'phone', 'dept', 'section', 'series')
    list_filter = ('dept', 'section', 'series')
    search_fields = ('roll', 'full_name', 'phone', 'dept', 'section', 'series')
    list_per_page = 25

admin.site.register(Student, StudentAdmin)