from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import Teacher
from departments.models import Department
from django.contrib.auth import authenticate

class loginForm(forms.Form):
    username = forms.CharField(required=True, help_text='Provide your code and department name in the format: code-dept_name')
    password = forms.CharField(widget=forms.PasswordInput, required=True)

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if not User.objects.filter(username=username).exists():
            raise forms.ValidationError('Username does not exist')
        return username
    def clean_password(self):
        username = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')
        user = authenticate(username=username, password=password)
        if user is None:
            raise forms.ValidationError('Invalid Password')
        return password
    
class verificationForm(forms.Form):
    code = forms.CharField(required=True, label='Teacher Code')
    dept_id = forms.CharField(required=True, label='Department Name', max_length=4)

    def clean(self):
        cleaned_data = super().clean()
        code = cleaned_data.get('code')
        dept_id = cleaned_data.get('dept_id')
        try:
            Teacher.objects.get(code=code, dept=Department.objects.get(dept_id=dept_id))
        except Teacher.DoesNotExist:
            raise forms.ValidationError('Invalid Code or Department')
        except Department.DoesNotExist:
            self.add_error('dept_id', 'Invalid Department')
            raise forms.ValidationError('Department is not found')
        return cleaned_data
    
class TeacherRegisterForm(UserCreationForm):
    username = forms.CharField(required=True, label='Username', max_length=30,  help_text='Please remember your username. It will be used to login', widget=forms.TextInput(attrs={'readonly': True}))
    code = forms.CharField(required=True, label='Teacher Code', max_length=5, widget=forms.TextInput(attrs={'readonly': True}))
    dept_id = forms.CharField(required=True, label='Department Name', max_length=4, widget=forms.TextInput(attrs={'readonly': True}))
    email = forms.EmailField(required=True, label='Email')
    
    class Meta:
        model = User
        fields = ['code','dept_id', 'username',  'first_name','last_name','email', 'password1', 'password2']
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.pop("autofocus", None)       

    def clean(self):
        cleaned_data = super().clean()
        code = cleaned_data.get('code')
        dept_id = cleaned_data.get('dept_id')
        try:
            Teacher.objects.get(code=code, dept=Department.objects.get(dept_id=dept_id))
            if f'{code}-{dept_id}' != cleaned_data.get('username'):
                raise forms.ValidationError('Invalid Format for Username')
        except Teacher.DoesNotExist:
            raise forms.ValidationError('Invalid Code or Department')
        except Department.DoesNotExist:
            raise forms.ValidationError('Invalid Department')
        return cleaned_data
    
    def save(self, commit=True) :
        user = super(TeacherRegisterForm, self).save(commit=False)
        user.username = self.cleaned_data['username']
        user.email = self.cleaned_data['email']
        teach = Teacher.objects.get(code=self.cleaned_data['code'], dept=Department.objects.get(dept_id=self.cleaned_data['dept_id']))
        
        if commit:
            user.save()
            teach.user = user
            teach.save()

        
        return user


    