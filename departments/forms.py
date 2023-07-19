from django import forms
from .models import *
from teachers.models import Teacher
import datetime as dt

class DeptLogin(forms.Form):
    department_name = forms.CharField(label='Department Name', 
                                      max_length=4, required=True)
    password = forms.CharField(label='Password', max_length=50, 
                               widget=forms.PasswordInput, required=True)

    def clean_department_name(self):
        department_name = self.cleaned_data['department_name']
        if not department_name:
            raise forms.ValidationError('Department name is required')
        return department_name
    

class addCourseForm(forms.ModelForm):
    semester = forms.IntegerField(min_value=1, max_value=8, required=True, label='Semester', 
                                   widget=forms.NumberInput(attrs={'placeholder': 'Enter semester number', 
                                                                   'title': 'Semester must be between 1 and 8'})) 
    class Meta:
        model = Course
        fields = ['title', 'name', 'type', 'credit']
        labels = {
            'title': 'Course Code',
            'name': 'Course Name',
            'type': 'Course Type',
            'credit': 'Course Credit'
        }
        widgets = {
            'title': forms.TextInput(attrs={'placeholder': 'Enter course code'}),
            'name': forms.TextInput(attrs={'placeholder': 'Enter course name'}),
            'type': forms.Select(attrs={'class': 'form-select'}),
            'credit': forms.NumberInput(attrs={'placeholder': 'Enter course credit'})
        }
    def clean_semester(self):
        semester = self.cleaned_data['semester']
        if semester < 1 or semester > 8:
            raise forms.ValidationError('Semester must be between 1 and 8')
        return semester
    def clean_credit(self):
        credit = self.cleaned_data['credit']
        if credit <= 0:
            raise forms.ValidationError('Course credit should be greater than 0')
        return credit
    
class addTeacherForm(forms.ModelForm):
    f_name = forms.CharField(label='First Name', max_length=50, required=True,
                             widget=forms.TextInput(attrs={'placeholder': 'Enter teacher First name'}))
    l_name = forms.CharField(label='Last Name', max_length=50, required=True,
                                widget=forms.TextInput(attrs={'placeholder': 'Enter teacher Last name'}))
    class Meta:
        model = Teacher
        fields = ['code', 'f_name','l_name', 'designation', 'intro']
        labels = {
            'code': 'Teacher Code',
            'designation': 'Designation', 
            'intro': 'Introduction'
        }
        
        
        widgets = {
            'code': forms.TextInput(attrs={'placeholder': 'Enter teacher code'}),
            'designation': forms.Select(attrs={'class': 'form-select'}),
            'intro': forms.Textarea(attrs={'placeholder': 'Enter teacher introduction', 'rows': 5})
        }
    def save(self, commit=True, *args, **kwargs):
        teacher = super(addTeacherForm, self).save(commit=False)
        teacher.first_name = self.cleaned_data['f_name']
        teacher.last_name = self.cleaned_data['l_name']
        teacher.dept = kwargs['dept']
        if commit:
            teacher.save() 
        return teacher

        
class addSeriesForm(forms.ModelForm):
    num_of_sections = forms.IntegerField(min_value=1, max_value=3, required=True, label='Number of Sections',  
                                      widget=forms.NumberInput(attrs={'placeholder': 'Enter number of sections',
                                                                        'title': 'Number of sections must be between 1 and 3'}))
    students_per_section = forms.IntegerField(min_value=1, max_value=60, required=True, label='Students per Section',
                                        widget=forms.NumberInput(attrs={'placeholder': 'Enter number of students per section',
                                                                        'title': 'Number of students per section must be greater than 0'}))
    class Meta:
        model = Series
        fields = ['name', 'num_of_sections', 'students_per_section', 'admit_year']
        labels = {
            'name': 'Series Name',
            'admit_year': 'Admission Year'
        }
        widgets = {
            'name': forms.TextInput(attrs={'placeholder': 'Enter series name'}),
            'admit_year': forms.NumberInput(attrs={'placeholder': 'Enter admission year'})
        }

    def clean_num_of_sections(self):
        num_of_sections = self.cleaned_data['num_of_sections']
        if num_of_sections < 1 or num_of_sections > 3:
            raise forms.ValidationError('Number of sections must be between 1 and 3')
        return num_of_sections
    def clean_students_per_section(self):
        students_per_section = self.cleaned_data['students_per_section']
        if students_per_section <= 0 or students_per_section > 60:
            raise forms.ValidationError('Number of students per section must be between 1 and 60')
        return students_per_section

    def save(self, commit=True, *args, **kwargs):
        series = super(addSeriesForm, self).save(commit=False)
        dept = kwargs['dept']
        series.department = dept
        # series.admit_year = dt.datetime.now().year
        no_of_sections = self.cleaned_data['num_of_sections']
        std_per_section = self.cleaned_data['students_per_section']
        series.maximum_students = no_of_sections * std_per_section
        series.running_semester = Semester.objects.get(id=1, dept=dept)
        if commit:
            series.save()
            for i in range(no_of_sections):
                Section.objects.create(name=f'{dept.dept_id}{series.admit_year-2000}{chr(i+65)}', series=series) # 65 is ascii value of 'A'
            courseRegistration.objects.create(series=series)
        return series