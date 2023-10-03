from django import forms
from django.contrib.auth.models import User
from django.contrib.auth import authenticate

class studentLoginForm(forms.Form):
    roll_no = forms.CharField(required=True, help_text='Provide your roll number', 
                              label='Roll Number')
    password = forms.CharField(widget=forms.PasswordInput, required=True)

    def clean_roll_no(self):
        roll_no = self.cleaned_data.get('roll_no')
        if not User.objects.filter(username=roll_no).exists():
            raise forms.ValidationError('Roll Number does not exist')
        return roll_no
    def clean_password(self):
        roll_no = self.cleaned_data.get('roll_no')
        password = self.cleaned_data.get('password')
        user = authenticate(username=roll_no, password=password)
        if user is None:
            raise forms.ValidationError('Invalid Password')
        return password