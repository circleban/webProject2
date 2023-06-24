from django import forms
from .models import Course
from teachers.models import Teacher
class DeptLogin(forms.Form):
    department_name = forms.CharField(label='Department Name', max_length=4, required=True)
    password = forms.CharField(label='Password', max_length=50, widget=forms.PasswordInput, required=True)

    def clean_department_name(self):
        department_name = self.cleaned_data['department_name']
        if not department_name:
            raise forms.ValidationError('Department name is required')
        return department_name
    

class addCourseForm(forms.ModelForm):
    class Meta:
        model = Course
        fields = ['title', 'name', 'type', 'semester', 'credit']
        labels = {
            'title': 'Course Code',
            'name': 'Course Name',
            'type': 'Course Type',
            'semester': 'Semester',
            'credit': 'Course Credit'
        }
        widgets = {
            'title': forms.TextInput(attrs={'placeholder': 'Enter course code'}),
            'name': forms.TextInput(attrs={'placeholder': 'Enter course name'}),
            'type': forms.Select(attrs={'class': 'form-select'}),
            'semester': forms.NumberInput(attrs={'placeholder': 'Enter semester number', 'title': 'Semester must be between 1 and 8'}),
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
    class Meta:
        model = Teacher
        fields = ['code', 'name', 'designation', 'intro']
        labels = {
            'code': 'Teacher Code',
            'name': 'Teacher Name',
            'designation': 'Designation',
            'intro': 'Introduction'
        }
        widgets = {
            'code': forms.TextInput(attrs={'placeholder': 'Enter teacher code'}),
            'name': forms.TextInput(attrs={'placeholder': 'Enter teacher name'}),
            'designation': forms.Select(attrs={'class': 'form-select'}),
            'intro': forms.Textarea(attrs={'placeholder': 'Enter teacher introduction', 'rows': 5})
        }
    

        