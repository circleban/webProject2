from typing import Any
from django import forms
from .models import *
from django.contrib.auth.models import User
from django.contrib.auth import authenticate


class paymentForm(forms.ModelForm):
    From = forms.CharField(required=True, max_length=20, label="Enter Your Username")
    To = forms.CharField(required=True, max_length=20, label="Enter Recipient's Username")
    password = forms.CharField(
        required=True,
        label="Enter your password",
        widget=forms.PasswordInput(
            attrs={
                "placeholder": "Enter your password",
                "title": "Enter your password to confirm the transaction",
                "autocomplete": "off",
            }
        ),
    )

    class Meta:
        model = Transaction
        fields = ["From", "To", "amount", "password"]
        labels = {"amount": "Amount"}
        widgets = {
            "amount": forms.NumberInput(attrs={"placeholder": "Enter amount"}),
        }

    def clean_From(self):
        paid_by = self.cleaned_data.get("From")
        print(paid_by)
        if not paid_by:
            raise forms.ValidationError("Paid by is required")
        if not User.objects.filter(username=paid_by).exists():
            raise forms.ValidationError("User does not exist")
        return paid_by

    def clean_password(self):
        password = self.cleaned_data.get("password")
        print(self.cleaned_data.get("From"))
        if not password:
            raise forms.ValidationError("Password is required")
        if not authenticate(username=self.cleaned_data.get("From"), password=password):
            raise forms.ValidationError("Incorrect Password")
        return password

    def clean_To(self):
        paid_to = self.cleaned_data.get("To")
        if not paid_to:
            raise forms.ValidationError("Paid to is required")
        if not User.objects.filter(username=paid_to).exists():
            raise forms.ValidationError("User does not exist")
        return paid_to

    def save(self, commit=True, *args, **kwargs):
        txn = super(paymentForm, self).save(commit=False)
        txn.paid_by = User.objects.get(username=self.cleaned_data.get("From"))
        txn.paid_to = User.objects.get(username=self.cleaned_data.get("To"))
        if commit:
            txn.save()
        return txn
